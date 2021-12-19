from typing import Iterable
from datetime import datetime
from app.produce.domain import DriverLocation


def _get_driver_locations() -> Iterable[DriverLocation]:
    return iter([
        DriverLocation(delivery_id=1, driver_id='1', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=2, driver_id='2', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=3, driver_id='1', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=4, driver_id='2', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=5, driver_id='1', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=6, driver_id='2', lat='-33.33', lng='122.22', timestamp=datetime.now()),
        DriverLocation(delivery_id=7, driver_id='1', lat='-33.33', lng='122.22', timestamp=datetime.now())
    ])


class MockDriverLocationProducer:
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def join(self):
        pass

    def get_driver_locations(self):
        return _get_driver_locations()
