import sys
import json
import time
import boto3
import argparse
import logging as log

from app.produce.producer import DriverLocationProducer
from app.common.json_encoder import DriverLocationJsonEncoder
from app.common.constants import KINESIS_DEFAULT_DELAY
from app.common.constants import KINESIS_DEFAULT_STREAM_NAME
from app.common.constants import KINESIS_DEFAULT_RECORDS_PER_REQUEST
from app.common.constants import PRODUCER_DEFAULT_DELAY
from app.produce.producer import PRODUCER_DEFAULT_MAX_THREADS
from app.produce.producer import PRODUCER_DEFAULT_BUFFER_SIZE


class KinesisDriverLocationConsumer:

    def __init__(self,
                 stream_name=KINESIS_DEFAULT_STREAM_NAME,
                 records_per_request=KINESIS_DEFAULT_RECORDS_PER_REQUEST,
                 delay=KINESIS_DEFAULT_DELAY,
                 producer_max_threads=PRODUCER_DEFAULT_MAX_THREADS,
                 producer_buffer_size=PRODUCER_DEFAULT_BUFFER_SIZE,
                 producer_delay=PRODUCER_DEFAULT_DELAY,
                 producer_no_api_key=False):
        self._kinesis = boto3.client('kinesis')
        self._delay = delay
        self._stream_name = stream_name
        self._records_per_request = records_per_request
        self._producer = DriverLocationProducer(buffer_size=producer_buffer_size,
                                                max_threads=producer_max_threads,
                                                delay=producer_delay,
                                                no_api_key=producer_no_api_key)

    def stream_locations_to_kinesis(self):
        self._producer.start()
        self._producer.join()

        request_count = 0
        total_locations = 0
        locations = []
        for location in self._producer.get_driver_locations():
            locations.append(location)
            total_locations += 1
            if len(locations) == self._records_per_request:
                self._send_locations(locations)
                request_count += 1
                locations.clear()
                time.sleep(self._delay)
        # send remaining locations
        if locations:
            self._send_locations(locations)
            request_count += 1

        log.info(f"Total Requests: {request_count}")
        log.info(f"Total Locations: {total_locations}")

    def _send_locations(self, locations):
        records = []
        for i in range(len(locations)):
            json_str = json.dumps(locations[i], cls=DriverLocationJsonEncoder)
            records.append({
                'Data': json_str.encode('utf-8'),
                'PartitionKey': f"partitionKey-{i}"
            })
        response = self._kinesis.put_records(StreamName=self._stream_name, Records=records)
        self._log_response(response)

    @staticmethod
    def _log_response(response):
        if log.getLogger().isEnabledFor(log.VERBOSE):
            log.verbose(json.dumps(response, indent=4))
        elif log.getLogger().isEnabledFor(log.DEBUG):
            del response['Records']
            log.debug(json.dumps(response, indent=4))
        else:
            response['RequestId'] = response['ResponseMetadata']['RequestId']
            response['StatusCode'] = response['ResponseMetadata']['HTTPStatusCode']
            response['RetryAttempts'] = response['ResponseMetadata']['RetryAttempts']
            del response['Records']
            del response['ResponseMetadata']
            log.info(response)


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
        self._parser.add_argument('--producer-max-threads', type=int, default=PRODUCER_DEFAULT_MAX_THREADS,
                                  help='producer maximum number of threads in thread pool (default 10)')
        self._parser.add_argument('--producer-buffer-size', type=int, default=PRODUCER_DEFAULT_BUFFER_SIZE,
                                  help='producer buffer size for driver locations (default 2000).')
        self._parser.add_argument('--producer-no-api-key', action='store_true',
                                  help='if there is no key, there needs to be points files present for every delivery')
        self._parser.add_argument('--producer-delay', type=float, default=PRODUCER_DEFAULT_DELAY,
                                  help='producer delay, in seconds, for each location into buffer (default 0.0)')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args


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


if __name__ == '__main__':
    main(sys.argv[1:])
