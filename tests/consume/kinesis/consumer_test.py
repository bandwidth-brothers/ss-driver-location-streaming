from app.consume.kinesis.streamer import KinesisStreamer
from app.consume.kinesis.consumer import KinesisDriverLocationConsumer
from tests.consume.kinesis.common import MockDriverLocationProducer


def test_kinesis_consumer_sets_producer_properties(monkeypatch, ctor_args):
    monkeypatch.setattr('app.consume.kinesis.consumer.DriverLocationProducer', ctor_args)

    KinesisDriverLocationConsumer(producer_max_threads=1,
                                  producer_buffer_size=2,
                                  producer_delay=0.5,
                                  producer_no_api_key=True)

    kwargs = ctor_args.get_kwargs()
    assert kwargs['geo'] is not None

    assert kwargs == {'geo': kwargs['geo'],
                      'max_threads': 1,
                      'buffer_size': 2,
                      'delay': 0.5}


def test_kinesis_consumer_calls_streamer_correct_number_of_times(monkeypatch, call_count):
    call_count.set_return_value(KinesisStreamer.Response(status=KinesisStreamer.Response.Status.SUCCESS, num_records=1))
    monkeypatch.setattr('app.consume.kinesis.consumer.DriverLocationProducer', MockDriverLocationProducer)
    monkeypatch.setattr('app.consume.kinesis.consumer.KinesisStreamer.send_locations', call_count)

    # if records_per_request is set to 2, there should be 4 calls, as there are 7 locations
    consumer = KinesisDriverLocationConsumer(delay=0, records_per_request=2, producer_no_api_key=True)
    consumer.stream_locations_to_kinesis()

    assert call_count.get_count() == 4
