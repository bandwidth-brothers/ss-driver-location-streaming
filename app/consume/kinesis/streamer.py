import json
import logging as log
import botocore.exceptions

from enum import Enum
from app.produce.domain import DriverLocation
from app.common.json_encoder import DriverLocationJsonEncoder
from app.consume.kinesis.failure import IFailureHandler


class KinesisStreamer:
    class Response:
        class Status(Enum):
            SUCCESS = 1
            FAILED = 2

        def __init__(self, status: Status, num_records: int):
            self._status = status
            self._num_records = num_records

        def get_status(self) -> Status:
            return self._status

        def get_num_records(self) -> int:
            return self._num_records

    @classmethod
    def send_locations(cls, kinesis, stream_name: str, locations: list[DriverLocation],
                       failure_handler: IFailureHandler) -> Response:
        records = []
        for i in range(len(locations)):
            json_str = json.dumps(locations[i], cls=DriverLocationJsonEncoder)
            records.append({
                'Data': json_str.encode('utf-8'),
                'PartitionKey': f"partitionKey-{i}"
            })
        try:
            response = kinesis.put_records(StreamName=stream_name, Records=records)
            cls.log_response(response)
            return cls.Response(cls.Response.Status.SUCCESS, len(records))
        except botocore.exceptions.ClientError as c_ex:
            log.info(f"Could not send records to Kinesis: {len(records)} records")
            log.debug(c_ex)
            failure_handler.handle_failure(locations)
            return cls.Response(cls.Response.Status.FAILED, len(records))

    @classmethod
    def log_response(cls, response):
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
