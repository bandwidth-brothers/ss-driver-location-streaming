import json
import time
import boto3
import logging as log

from app.produce.producer import DriverLocationProducer
from app.common.json_encoder import DriverLocationJsonEncoder
from app.common.constants import KINESIS_DEFAULT_DELAY
from app.common.constants import KINESIS_DEFAULT_STREAM_NAME
from app.common.constants import KINESIS_DEFAULT_RECORDS_PER_REQUEST
from app.produce.producer import PRODUCER_DEFAULT_MAX_THREADS
from app.produce.producer import PRODUCER_DEFAULT_BUFFER_SIZE


class KinesisDriverLocationConsumer:

    def __init__(self,
                 stream_name=KINESIS_DEFAULT_STREAM_NAME,
                 records_per_request=KINESIS_DEFAULT_RECORDS_PER_REQUEST,
                 delay=KINESIS_DEFAULT_DELAY,
                 producer_max_threads=PRODUCER_DEFAULT_MAX_THREADS,
                 producer_buffer_size=PRODUCER_DEFAULT_BUFFER_SIZE,
                 producer_no_api_key=False):
        self._client = boto3.client('kinesis')
        self._delay = delay
        self._stream_name = stream_name
        self._records_per_request = records_per_request
        self._producer = DriverLocationProducer(buffer_size=producer_buffer_size,
                                                max_threads=producer_max_threads,
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
        response = self._client.put_records(StreamName=self._stream_name, Records=records)
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
