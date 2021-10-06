import argparse
import logging as log

from app.consume.kinesis import KinesisDriverLocationConsumer,\
    DEFAULT_DELAY, DEFAULT_STREAM_NAME, DEFAULT_RECORDS_PER_REQUEST


def main(_args):
    parser = argparse.ArgumentParser(description="Stream driver location data to Kinesis")
    parser.add_argument('-n', '--stream-name', type=str, help='name of the Kinesis stream',
                        default=DEFAULT_STREAM_NAME)
    parser.add_argument('-l', '--log', type=str, help='log level (VERBOSE, DEBUG, INFO ←, WARN, ERROR)',
                        default='INFO')
    parser.add_argument('-r', '--records-per-request', type=int, help='record to send per request to Kinesis',
                        default=DEFAULT_RECORDS_PER_REQUEST)
    parser.add_argument('-d', '--delay', type=float, help='delay for each request to Kinesis',
                        default=DEFAULT_DELAY)
    parser.add_argument('-v', '--verbose', action='store_true', help='same as --log VERBOSE')
    args = parser.parse_args(_args)

    if args.verbose:
        log.basicConfig(level=log.VERBOSE)
    else:
        log.basicConfig(level=args.log)

    KinesisDriverLocationConsumer(stream_name=args.stream_name,
                                  records_per_request=args.records_per_request,
                                  delay=args.delay) \
        .stream_locations_to_kinesis()
