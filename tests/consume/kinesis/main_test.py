from app.consume.kinesis.main import main
from app.consume.kinesis.failure import FileFailureHandler
from app.consume.kinesis.failure import SqsQueueFailureHandler


def test_main_correct_arguments(monkeypatch, ctor_args, call_count):
    monkeypatch.setattr('app.consume.kinesis.main.KinesisDriverLocationConsumer.__new__', ctor_args)
    ctor_args.stream_locations_to_kinesis = call_count

    main(['--stream-name', 'TestStream',
          '--records-per-request', '10',
          '--delay', '0.5',
          '--producer-buffer-size', '10000',
          '--producer-max-threads', '2',
          '--producer-delay', '0.1',
          '--producer-no-api-key'])

    kwargs = ctor_args.get_kwargs()
    del kwargs['failure_handler']

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


def test_main_correct_failure_handler(monkeypatch, ctor_args):
    monkeypatch.setattr('app.consume.kinesis.main.KinesisDriverLocationConsumer.__new__', ctor_args)
    ctor_args.stream_locations_to_kinesis = lambda _: None

    main(['--failure-handler', 'sqs'])
    kwargs = ctor_args.get_kwargs()

    failure_handler = kwargs['failure_handler']
    assert type(failure_handler) == SqsQueueFailureHandler

    main([])
    kwargs = ctor_args.get_kwargs()

    failure_handler = kwargs['failure_handler']
    assert type(failure_handler) == FileFailureHandler
