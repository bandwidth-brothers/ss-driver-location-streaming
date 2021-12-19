import json
import boto3
import pytest

from app.consume.kinesis.streamer import KinesisStreamer
from app.consume.kinesis.failure import NoopFailureHandler
from tests.consume.kinesis.common import _get_driver_locations


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
    monkeypatch.setattr('app.consume.kinesis.streamer.KinesisStreamer.log_response', lambda response: None)
    kinesis = boto3.client('kinesis')
    kinesis.put_records = records_collector

    KinesisStreamer.send_locations(kinesis, 'TestStream', list(_get_driver_locations()), NoopFailureHandler())

    records = records_collector.get_records()
    assert len(records) == 7

    def _get_delivery_id_from_record(record):
        data_str = record['Data'].decode('utf-8')
        data_dict = json.loads(data_str)
        return data_dict['delivery_id']

    delivery_ids = list(map(_get_delivery_id_from_record, records))
    for _id in [1, 2, 3, 4, 5, 6, 7]:
        assert _id in delivery_ids
