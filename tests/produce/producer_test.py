from functools import reduce
from app.produce.domain import Driver
from app.produce.producer import DeliveryManager
from app.produce.producer import DriverLocationProducer
from tests.produce.common import _get_drivers_list


def test_delivery_manager_init(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    assert isinstance(manager.get_driver('1'), Driver)
    assert isinstance(manager.get_driver('2'), Driver)


def test_delivery_manager_get_driver(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    driver = manager.get_driver('2')
    assert driver is not None
    assert len(driver.deliveries) == 2


def test_delivery_manager_complete_current_delivery(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    delivery = manager.get_delivery('2')
    assert delivery is not None
    assert delivery.is_complete() is False
    assert delivery.address.street == '667 Awesome St'

    driver = manager.get_driver('2')
    assert driver.current_location.street == '321 MLK Blvd'

    manager.complete_driver_delivery('2')
    assert delivery.is_complete()
    assert driver.current_location.street == '667 Awesome St'


def test_delivery_manager_get_delivery(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    delivery = manager.get_delivery('2')
    assert delivery is not None

    driver = manager.get_driver('2')
    assert delivery == driver.current_delivery

    manager.complete_driver_delivery('2')
    manager.get_delivery('2')
    assert driver.has_more_deliveries() is False


def test_driver_location_producer_get_driver_locations(monkeypatch, caplog):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    monkeypatch.setattr('app.produce.geo.DEFAULT_POINTS_DIR', 'tests/files')
    producer = DriverLocationProducer()
    producer.start()
    producer.join()

    locations = {}
    for location in producer.get_driver_locations():
        driver_id = location.driver_id
        if driver_id not in locations:
            locations[driver_id] = 0
        locations[driver_id] += 1

    total_points = reduce(lambda tot, val: tot + val, locations.values(), 0)
    assert total_points == 28

    assert locations['1'] == 10
    assert locations['2'] == 18
