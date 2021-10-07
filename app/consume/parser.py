import argparse

from app.common.constants import\
    KINESIS_DEFAULT_DELAY,\
    KINESIS_DEFAULT_STREAM_NAME,\
    KINESIS_DEFAULT_RECORDS_PER_REQUEST,\
    PRODUCER_DEFAULT_MAX_THREADS,\
    PRODUCER_DEFAULT_BUFFER_SIZE


class KinesisConsumerArgParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(description="Stream driver location data to Kinesis")
        self._parser.add_argument('-n', '--stream-name', type=str, help='name of the Kinesis stream',
                                  default=KINESIS_DEFAULT_STREAM_NAME)
        self._parser.add_argument('-l', '--log', type=str, help='log level (VERBOSE, DEBUG, INFO ←, WARN, ERROR)',
                                  default='INFO')
        self._parser.add_argument('-r', '--records-per-request', type=int, help='record to send per request to Kinesis',
                                  default=KINESIS_DEFAULT_RECORDS_PER_REQUEST)
        self._parser.add_argument('-d', '--delay', type=float, help='delay for each request to Kinesis',
                                  default=KINESIS_DEFAULT_DELAY)
        self._parser.add_argument('-v', '--verbose', action='store_true', help='same as --log VERBOSE')
        self._parser.add_argument('--producer-max-threads', type=int, default=PRODUCER_DEFAULT_MAX_THREADS,
                                  help='maximum number of threads in thread pool (default 10)')
        self._parser.add_argument('--producer-buffer-size', type=int, default=PRODUCER_DEFAULT_BUFFER_SIZE,
                                  help='buffer size for driver locations (default 2000).')
        self._parser.add_argument('--producer-no-api-key', action='store_true',
                                  help='if there is no key, there needs to be points files present for every delivery')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args
