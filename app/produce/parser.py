
import argparse
import logging as log
import sys

from argparse import RawTextHelpFormatter
from app.produce.constants import PRODUCER_DEFAULT_BUFFER_SIZE
from app.produce.constants import PRODUCER_DEFAULT_MAX_THREADS

class DriverLocationParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                               description="""Generate driver location geolocation data.
                                              
Driver location data can be from Deliveries in a database. The location data
can be output to a file in different formats or can be consumed by a Python
client. This utility allows the user to save the location data to file or to
print the data to the terminal. Or a summary of the output can be printed.

examples:
    python -m app.produce.producer --csv out_file.csv
    python -m app.produce.producer --json out_file.json
    python -m app.produce.producer --sum
    python -m app.produce.producer --print-all""")

        self._parser.add_argument('--sum', action='store_true', help='print a summary of the location data (default)')
        self._parser.add_argument('--print-all', action='store_true', help='print all locations')
        self._parser.add_argument('--csv', type=str, help='save the location data to a csv file')
        self._parser.add_argument('--json', type=str, help='save the location data to a json file')
        self._parser.add_argument('--log', type=str, default=log.INFO,
                                  help='the log level (VERBOSE, DEBUG, INFO ←, WARN, ERROR)')
        self._parser.add_argument('-v', '--verbose', action='store_true', help='same as --log VERBOSE')
        self._parser.add_argument('--max-threads', type=int, default=PRODUCER_DEFAULT_MAX_THREADS,
                                  help='maximum number of threads in thread pool (default 10)')
        self._parser.add_argument('--buffer-size', type=int, default=PRODUCER_DEFAULT_BUFFER_SIZE,
                                  help='buffer size for driver locations (default 2000).')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args


if __name__ == '__main__':
    args = DriverLocationParser(sys.argv[1:]).get_args()
    print(args)
