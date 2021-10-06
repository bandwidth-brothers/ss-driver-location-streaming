import pytest

from typing import Iterable
from app.produce.domain import DriverLocation
from app.consume.kinesis import KinesisDriverLocationConsumer


def _get_driver_locations() -> Iterable[DriverLocation]:
    return iter([
        DriverLocation(delivery_id=1, driver_id='1', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=2, driver_id='2', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=3, driver_id='1', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=4, driver_id='2', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=5, driver_id='1', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=6, driver_id='2', lat='-33.33', lng='122.22'),
        DriverLocation(delivery_id=7, driver_id='1', lat='-33.33', lng='122.22')
    ])


class MockDriverLocationProducer:

    def start(self):
        pass

    def join(self):
        pass

    # noinspection PyMethodMayBeStatic
    def get_driver_locations(self):
        return _get_driver_locations()


def test_stream_locations_to_kinesis_request_count(monkeypatch, call_count, caplog):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer', MockDriverLocationProducer)
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer._send_locations', call_count)

    # if records_per_request is set to 2, there should be 4 calls, as there are 7 locations
    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2)
    consumer.stream_locations_to_kinesis()

    assert call_count.get_count() == 4


@pytest.fixture
def records_collector():
    class RecordsCollector:
        __records = []

        def __call__(self, *args, **kwargs):
            self.__records += kwargs['Records']

        def get_records(self):
            return self.__records
    return RecordsCollector()


def test_stream_locations_to_kinesis_all_locations_sent(monkeypatch, records_collector, caplog):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer', MockDriverLocationProducer)
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer._log_response', lambda _self, res: None)

    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2)
    consumer.client.put_records = records_collector
    consumer.stream_locations_to_kinesis()

    assert len(records_collector.get_records()) == 7
