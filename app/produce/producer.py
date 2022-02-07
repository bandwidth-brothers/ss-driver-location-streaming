import time
import datetime
import logging as log
import traceback

from queue import Queue
from typing import Optional, Iterable
from functools import reduce
from threading import Lock, Thread
from concurrent.futures import ThreadPoolExecutor
from app.produce.geo import IGeo
from app.produce.domain import Driver
from app.produce.domain import Delivery
from app.produce.domain import DriverLocation
from app.data.deliveries import Deliveries
from app.common.constants import PRODUCER_DEFAULT_DELAY
from app.common.constants import PRODUCER_DEFAULT_BUFFER_SIZE
from app.common.constants import PRODUCER_DEFAULT_MAX_THREADS
from app.common.constants import GEO_DEFAULT_DATA_DIR


class DeliveryManager:
    def __init__(self):
        def map_drivers_ids(driver_dict, driver) -> dict[str: Driver]:
            driver_dict[driver.id] = driver
            return driver_dict

        drivers = Deliveries.get_driver_deliveries()
        if len(drivers) == 0:
            log.warning('There are no deliveries in the database.')

        self._drivers_map = reduce(map_drivers_ids, drivers, {})
        self._lock = Lock()

    def get_driver(self, driver_id) -> Optional[Driver]:
        if driver_id in self._drivers_map:
            return self._drivers_map[driver_id]
        else:
            return None

    def deliveries_complete(self) -> bool:
        return not self._drivers_map

    def get_delivery(self, driver_id) -> Optional[Delivery]:
        """
        Retrieves a delivery from the driver dict. When there are no
        more deliveries for the driver, the driver will be deleted
        from the dict.
        """
        with self._lock:
            if driver_id not in self._drivers_map:
                return None

            driver = self._drivers_map[driver_id]
            if driver.has_active_delivery():
                if not driver.is_current_delivery_complete():
                    return None

            if not driver.has_more_deliveries():
                del self._drivers_map[driver_id]
                return None

            delivery = driver.get_next_delivery()
            driver.set_current_delivery(delivery)

        return delivery

    def complete_driver_delivery(self, driver_id: str):
        """
        Complete the current delivery for a driver. When this is set,
        the current address/location for the driver will be set to
        the address of the delivery.
        """
        with self._lock:
            driver = self._drivers_map[driver_id]
            driver.complete_current_delivery()
            driver.set_current_location(driver.current_delivery.address)

    def get_drivers_ids(self) -> list[str]:
        return list(self._drivers_map.keys())


class DriverLocationProducer:
    def __init__(self,
                 geo: IGeo,
                 buffer_size: int = PRODUCER_DEFAULT_BUFFER_SIZE,
                 max_threads: int = PRODUCER_DEFAULT_MAX_THREADS,
                 delay: float = PRODUCER_DEFAULT_DELAY):
        self._delivery_manager = DeliveryManager()
        self._location_buffer = Queue(maxsize=buffer_size)
        self._geo = geo
        self._producer_thread = None
        self._lock = Lock()
        self._max_threads = max_threads
        self._delay = delay

    def _get_timestamp(self, increment):
        now = datetime.datetime.now()
        return now + datetime.timedelta(0, increment * 3)

    def _process_delivery(self, delivery: Delivery, driver_id):
        try:
            driver = self._delivery_manager.get_driver(driver_id)
            plan = self._geo.get_points(driver, delivery)
            points = plan.points

            Deliveries.set_delivery_picked_up_at(delivery.id, self._get_timestamp(0))
            for i in range(len(points)):
                point = points[i]
                location = DriverLocation(delivery_id=delivery.id, driver_id=driver_id,
                                          lat=point['lat'], lng=point['lng'], timestamp=self._get_timestamp(i))
                self._location_buffer.put(location)
                if self._delay:
                    time.sleep(self._delay)

            self._delivery_manager.complete_driver_delivery(driver_id)
            log.info(f"Driver: {driver_id}, Delivery: {delivery.id}, Points: {len(plan.points)}")
        except Exception:
            log.error('Could not complete processing delivery')
            traceback.print_exc()

    def _produce(self):
        driver_ids = self._delivery_manager.get_drivers_ids()

        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            while not self._delivery_manager.deliveries_complete():
                for driver_id in driver_ids:
                    delivery = self._delivery_manager.get_delivery(driver_id)
                    if delivery is not None:
                        executor.submit(self._process_delivery, delivery, driver_id)
            log.info("All deliveries complete.")

    def start(self):
        """
        Start the producer. This method must be called before calling
        get_driver_locations().
        """
        if not self._producer_thread:
            self._producer_thread = Thread(target=self._produce, daemon=True)
            self._producer_thread.start()

    def join(self):
        """
        Join the producer thread and the buffer. If this is not called,
        the produce may not emit all locations from the buffer and cause
        the program to hang.
        """
        self._location_buffer.join()

    def get_driver_locations(self) -> Iterable[DriverLocation]:
        """
        A generator function that produces driver location data.
        Usage:
            for location in generator.get_driver_locations():
                print(location)
        """
        while not self._delivery_manager.deliveries_complete()\
                or not self._location_buffer.empty():
            with self._lock:
                if not self._location_buffer.empty():
                    location = self._location_buffer.get()
                    self._location_buffer.task_done()
                    log.verbose(f"DriverLocation: {location}")
                    yield location
                else:
                    continue
        log.debug(f"Queue size: {self._location_buffer.qsize()}")
