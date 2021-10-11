from app.consume.main import main


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
