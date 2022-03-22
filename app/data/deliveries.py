import json
import random

from datetime import datetime
from functools import reduce
from app.config import Config
from app.db.database import Database
from app.produce.domain import Driver
from app.produce.domain import Address
from app.produce.domain import Delivery


class Deliveries:

    @staticmethod
    def _create_delivery_from_result(res) -> Delivery:
        address = Address(street=res[2], city=res[3], state=res[4], zip_code=res[5])
        return Delivery(deliv_id=res[0], driver_id=res[1], address=address)

    @staticmethod
    def get_driver_deliveries() -> list[Driver]:
        db = Database(Config())
        results = db.run_query('SELECT de.id, HEX(dr.id), line1, city, state, zip '
                               'FROM delivery de JOIN address a ON de.address_id = a.id '
                               'JOIN driver dr ON dr.id = de.driver_Id')
        deliveries = list(map(Deliveries._create_delivery_from_result, results))

        def _map_deliveries_to_driver(driver_dict: dict, delivery):
            _driver_id = delivery.driver_id
            if _driver_id not in driver_dict:
                driver_dict[_driver_id] = []
            driver_dict[_driver_id].append(delivery)
            return driver_dict

        driver_deliveries = reduce(_map_deliveries_to_driver, deliveries, {})

        drivers: list[Driver] = []
        start_locations = Deliveries._get_driver_start_locations()
        for driver_id in driver_deliveries:
            driver = Driver(driver_id=driver_id, current_location=random.choice(start_locations),
                            deliveries=driver_deliveries[driver_id])
            drivers.append(driver)

        return drivers

    class AddressJsonDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=Deliveries.AddressJsonDecoder._object_hook, *args, **kwargs)

        @classmethod
        def _object_hook(cls, dct):
            if 'lat' in dct:
                return None
            return Address(street=dct['address1'], city=dct['city'], state=dct['state'], zip_code=dct['postalCode'])

    @staticmethod
    def _get_driver_start_locations() -> list[Address]:
        with open('data/driver-start-locations.json') as f:
            addresses = json.load(f, cls=Deliveries.AddressJsonDecoder)
        return addresses

    @staticmethod
    def set_delivery_picked_up_at(delivery_id: int, timestamp: datetime):
        """"
        Set the delivery picked_up_at field in the database

        :param delivery_id: the id of the delivery
        :param timestamp: the time the delivery was picked up at
        :raises jaydebeapi.DatabaseError: if there is a database related problem
        """
        db = Database(Config())
        db.update('UPDATE delivery SET picked_up_at = ? WHERE id = ?', (timestamp.isoformat(), delivery_id))
