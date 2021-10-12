import json
import pytest

from typing import Iterable
from app.produce.domain import DriverLocation
from app.consume.kinesis import main
from app.consume.kinesis import KinesisDriverLocationConsumer


def test_kinesis_consumer_sets_producer_properties(monkeypatch, ctor_args):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer', ctor_args)

    KinesisDriverLocationConsumer(producer_max_threads=1,
                                  producer_buffer_size=2,
                                  producer_delay=0.5,
                                  producer_no_api_key=True)

    kwargs = ctor_args.get_kwargs()
    assert kwargs == {'max_threads': 1,
                      'buffer_size': 2,
                      'delay': 0.5,
                      'no_api_key': True}


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
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def join(self):
        pass

    def get_driver_locations(self):
        return _get_driver_locations()


def test_stream_locations_to_kinesis_request_count(monkeypatch, call_count):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer', MockDriverLocationProducer)
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer._send_locations', call_count)

    # if records_per_request is set to 2, there should be 4 calls, as there are 7 locations
    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2, producer_no_api_key=True)
    consumer.stream_locations_to_kinesis()

    assert call_count.get_count() == 4


def test_stream_locations_to_kinesis_no_locations(monkeypatch, call_count):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer.get_driver_locations', lambda _self: [])
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer._send_locations', call_count)

    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2, producer_no_api_key=True)
    consumer.stream_locations_to_kinesis()

    assert call_count.get_count() == 0


@pytest.fixture
def records_collector():
    class RecordsCollector:
        __records = []

        def __call__(self, *args, **kwargs):
            self.__records += kwargs['Records']

        def get_records(self):
            return self.__records
    return RecordsCollector()


def test_stream_locations_to_kinesis_all_locations_sent(monkeypatch, records_collector):
    monkeypatch.setattr('app.consume.kinesis.DriverLocationProducer', MockDriverLocationProducer)
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer._log_response', lambda _self, res: None)
    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2)
    consumer._kinesis.put_records = records_collector

    consumer.stream_locations_to_kinesis()

    records = records_collector.get_records()
    assert len(records) == 7

    def _get_delivery_id_from_record(record):
        data_str = record['Data'].decode('utf-8')
        data_dict = json.loads(data_str)
        return data_dict['delivery_id']

    delivery_ids = list(map(_get_delivery_id_from_record, records))
    for _id in [1, 2, 3, 4, 5, 6, 7]:
        assert _id in delivery_ids


def test_consume_main_correct_arguments(monkeypatch, ctor_args, call_count):
    monkeypatch.setattr('app.consume.kinesis.KinesisDriverLocationConsumer.__new__', ctor_args)
    ctor_args.stream_locations_to_kinesis = call_count

    main(['--stream-name', 'TestStream',
          '--records-per-request', '10',
          '--delay', '0.5',
          '--producer-buffer-size', '10000',
          '--producer-max-threads', '2',
          '--producer-delay', '0.1',
          '--producer-no-api-key'])

    kwargs = ctor_args.get_kwargs()
    assert kwargs == {
        'stream_name': 'TestStream',
        'records_per_request': 10,
        'delay': 0.5,
        'producer_buffer_size': 10000,
        'producer_max_threads': 2,
        'producer_delay': 0.1,
        'producer_no_api_key': True
    }
    assert call_count.get_count() == 1
