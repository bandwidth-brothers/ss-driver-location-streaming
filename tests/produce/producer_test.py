import logging

from functools import reduce
from app.produce.geo import GoogleMapsGeo
from app.produce.domain import Driver
from app.produce.producer import DeliveryManager
from app.produce.producer import DriverLocationProducer
from tests.produce.common import _get_drivers_list


def test_delivery_manager_init(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    assert isinstance(manager.get_driver(driver_id='1'), Driver)
    assert isinstance(manager.get_driver(driver_id='2'), Driver)


def test_delivery_manager_get_driver(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    driver = manager.get_driver(driver_id='2')
    assert driver is not None
    assert len(driver.deliveries) == 2


def test_delivery_manager_complete_current_delivery_and_driver_location_set(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    delivery = manager.get_delivery(driver_id='2')
    assert delivery is not None
    assert delivery.is_complete() is False
    assert delivery.address.street == '667 Awesome St'

    driver = manager.get_driver(driver_id='2')
    assert driver.current_location.street == '321 MLK Blvd'

    manager.complete_driver_delivery(driver_id='2')
    assert delivery.is_complete()
    assert driver.current_location.street == '667 Awesome St'


def test_delivery_manager_get_multiple_deliveries_from_driver_with_complete(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    first_delivery = manager.get_delivery(driver_id='2')
    assert first_delivery is not None

    driver = manager.get_driver(driver_id='2')
    assert first_delivery == driver.current_delivery

    manager.complete_driver_delivery(driver_id='2')
    next_delivery = manager.get_delivery(driver_id='2')

    assert next_delivery != first_delivery
    assert driver.has_more_deliveries() is False


def test_delivery_manager_get_multiple_deliveries_from_driver_without_complete(monkeypatch):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    manager = DeliveryManager()

    delivery = manager.get_delivery(driver_id='2')
    assert delivery is not None

    driver = manager.get_driver(driver_id='2')
    assert delivery == driver.current_delivery

    next_delivery = manager.get_delivery(driver_id='2')
    assert next_delivery is None
    assert driver.has_more_deliveries() is True


def test_driver_location_producer_get_driver_locations(monkeypatch, caplog):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    monkeypatch.setattr('app.produce.producer.Deliveries.set_delivery_picked_up_at', lambda a, b: None)
    caplog.set_level(logging.INFO)

    geo = GoogleMapsGeo(no_api_key=True, data_dir='tests/files')
    producer = DriverLocationProducer(geo=geo)
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
