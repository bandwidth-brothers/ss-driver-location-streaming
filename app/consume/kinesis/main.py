import sys
import logging as log

from app.config import Config
from app.consume.kinesis.parser import KinesisConsumerArgParser
from app.consume.kinesis.failure import FileFailureHandler
from app.consume.kinesis.failure import NoopFailureHandler
from app.consume.kinesis.failure import SqsQueueFailureHandler
from app.consume.kinesis.consumer import KinesisDriverLocationConsumer


def main(_args):
    args = KinesisConsumerArgParser(_args).get_args()

    if args.verbose:
        log.basicConfig(level=log.VERBOSE)
    else:
        log.basicConfig(level=args.log)

    failure_handler_arg = args.failure_handler
    if failure_handler_arg == 'file':
        failure_handler = FileFailureHandler(directory=args.failure_dir)
    elif failure_handler_arg == 'sqs':
        config = Config()
        if config.failover_queue_url is None:
            log.error('FAILOVER_QUEUE_URL environment variable is not set.')
            sys.exit(1)
        failure_handler = SqsQueueFailureHandler(queue_url=config.failover_queue_url)
    elif failure_handler_arg == 'noop':
        failure_handler = NoopFailureHandler()
    else:
        log.error(f"{failure_handler_arg} is not a valid failure handler.")
        sys.exit(1)

    consumer = KinesisDriverLocationConsumer(stream_name=args.stream_name,
                                             records_per_request=args.records_per_request,
                                             delay=args.delay,
                                             producer_buffer_size=args.producer_buffer_size,
                                             producer_max_threads=args.producer_max_threads,
                                             producer_delay=args.producer_delay,
                                             producer_no_api_key=args.producer_no_api_key,
                                             producer_no_gapi=args.producer_no_gapi,
                                             failure_handler=failure_handler)
    consumer.stream_locations_to_kinesis()
