import argparse

from app.common.constants import KINESIS_DEFAULT_DELAY
from app.common.constants import KINESIS_DEFAULT_STREAM_NAME
from app.common.constants import KINESIS_DEFAULT_FAILURE_DIR
from app.common.constants import KINESIS_DEFAULT_RECORDS_PER_REQUEST
from app.common.constants import PRODUCER_DEFAULT_DELAY
from app.produce.producer import PRODUCER_DEFAULT_MAX_THREADS
from app.produce.producer import PRODUCER_DEFAULT_BUFFER_SIZE


class KinesisConsumerArgParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(prog='app.consume.kinesis', description="Stream driver location data to Kinesis")
        self._parser.add_argument('-n', '--stream-name', type=str, help='name of the Kinesis stream',
                                  default=KINESIS_DEFAULT_STREAM_NAME)
        self._parser.add_argument('-l', '--log', type=str, help='log level (VERBOSE, DEBUG, INFO ←, WARN, ERROR)',
                                  default='INFO')
        self._parser.add_argument('-r', '--records-per-request', type=int, help='record to send per request to Kinesis',
                                  default=KINESIS_DEFAULT_RECORDS_PER_REQUEST)
        self._parser.add_argument('-d', '--delay', type=float, help='delay for each request to Kinesis (default 0.2)',
                                  default=KINESIS_DEFAULT_DELAY)
        self._parser.add_argument('-v', '--verbose', action='store_true', help='same as --log VERBOSE')
        self._parser.add_argument('--failure-handler', type=str, choices=['sqs', 'file', 'noop'], default='file',
                                  help='failure handler when location streaming fails (default \'file\')')
        self._parser.add_argument('--failure-dir', type=str, default=KINESIS_DEFAULT_FAILURE_DIR,
                                  help='directory to send locations on streaming failure')
        self._parser.add_argument('--producer-max-threads', type=int, default=PRODUCER_DEFAULT_MAX_THREADS,
                                  help='producer maximum number of threads in thread pool (default 10)')
        self._parser.add_argument('--producer-buffer-size', type=int, default=PRODUCER_DEFAULT_BUFFER_SIZE,
                                  help='producer buffer size for driver locations (default 2000).')
        self._parser.add_argument('--producer-no-api-key', action='store_true',
                                  help='if there is no key, there needs to be points files present for every delivery')
        self._parser.add_argument('--producer-no-gapi', action='store_true',
                                  help='producer use random generate geolocations without the need for Google API')
        self._parser.add_argument('--producer-delay', type=float, default=PRODUCER_DEFAULT_DELAY,
                                  help='producer delay, in seconds, for each location into buffer (default 0.0)')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args
