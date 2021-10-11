import logging as log

from app.consume.parser import KinesisConsumerArgParser
from app.consume.kinesis import KinesisDriverLocationConsumer


def main(_args):
    args = KinesisConsumerArgParser(_args).get_args()

    if args.verbose:
        log.basicConfig(level=log.VERBOSE)
    else:
        log.basicConfig(level=args.log)

    consumer = KinesisDriverLocationConsumer(stream_name=args.stream_name,
                                             records_per_request=args.records_per_request,
                                             delay=args.delay,
                                             producer_buffer_size=args.producer_buffer_size,
                                             producer_max_threads=args.producer_max_threads,
                                             producer_delay=args.producer_delay,
                                             producer_no_api_key=args.producer_no_api_key)
    consumer.stream_locations_to_kinesis()
