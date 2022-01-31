import argparse
import logging as log

from argparse import RawTextHelpFormatter
from app.common.constants import GEO_DEFAULT_DATA_DIR
from app.common.constants import PRODUCER_DEFAULT_DELAY
from app.common.constants import PRODUCER_DEFAULT_BUFFER_SIZE
from app.common.constants import PRODUCER_DEFAULT_MAX_THREADS


class DriverLocationParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(prog='app.produce', formatter_class=RawTextHelpFormatter,
                                               description="""Generate driver location geolocation data.
                                              
Driver location data can be from Deliveries in a database. The location data
can be output to a file in different formats or can be consumed by a Python
client. This utility allows the user to save the location data to file or to
print the data to the terminal. Or a summary of the output can be printed.

The GOOGLE_API_KEY environment variable needs to be set to make Maps API calls.

examples:
    python -m app.produce
    python -m app.produce --log DEBUG --data-dir ./tmp
    python -m app.produce --max-threads 5 --buffer-size 3000
    python -m app.produce --make-maps --data-dir ./tmp""")

        self._parser.add_argument('--log', type=str, default=log.INFO,
                                  help='the log level (VERBOSE, DEBUG, INFO ←, WARN, ERROR)')
        self._parser.add_argument('-v', '--verbose', action='store_true', help='same as --log VERBOSE')
        self._parser.add_argument('--max-threads', type=int, default=PRODUCER_DEFAULT_MAX_THREADS,
                                  help='maximum number of threads in thread pool (default 10)')
        self._parser.add_argument('--buffer-size', type=int, default=PRODUCER_DEFAULT_BUFFER_SIZE,
                                  help='buffer size for driver locations (default 2000).')
        self._parser.add_argument('--no-api-key', action='store_true',
                                  help='if there is no key, there needs to be points files present for every delivery')
        self._parser.add_argument('--make-maps', action='store_true',
                                  help='make static maps from points files')
        self._parser.add_argument('--data-dir', type=str, default=GEO_DEFAULT_DATA_DIR,
                                  help='directory for points files and static maps (default ./tmp)')
        self._parser.add_argument('--delay', type=float, default=PRODUCER_DEFAULT_DELAY,
                                  help='delay, in seconds, for each location into buffer (default 0.01)')
        self._parser.add_argument('--no-gapi', action='store_true',
                                  help='use random generate geolocations without the need for Google API')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args
