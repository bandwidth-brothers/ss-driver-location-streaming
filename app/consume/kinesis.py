import json
import time
import boto3
import logging as log

from app.produce.producer import DriverLocationProducer
from app.common.json_encoder import DriverLocationJsonEncoder


DEFAULT_RECORDS_PER_REQUEST = 100
DEFAULT_STREAM_NAME = 'DriverLocationStream'
DEFAULT_DELAY = 0.3


class KinesisDriverLocationConsumer:

    def __init__(self,
                 stream_name=DEFAULT_STREAM_NAME,
                 records_per_request=DEFAULT_RECORDS_PER_REQUEST,
                 delay=DEFAULT_DELAY):
        self.client = boto3.client('kinesis')
        self.delay = delay
        self.stream_name = stream_name
        self.records_per_request = records_per_request

    def stream_locations_to_kinesis(self):
        producer = DriverLocationProducer()
        producer.start()
        producer.join()

        request_count = 0
        total_locations = 0
        locations = []
        for location in producer.get_driver_locations():
            locations.append(location)
            total_locations += 1
            if len(locations) == self.records_per_request:
                self._send_locations(locations)
                request_count += 1
                locations.clear()
                time.sleep(self.delay)
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
        response = self.client.put_records(StreamName=self.stream_name, Records=records)
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
