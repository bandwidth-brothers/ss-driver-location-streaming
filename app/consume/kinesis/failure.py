import abc
import json
import pathlib
import os.path

import boto3
import logging as log
import botocore.exceptions

from abc import abstractmethod
from pathlib import Path
from datetime import date
from datetime import datetime
from app.produce.domain import DriverLocation
from app.common.json_encoder import DriverLocationJsonEncoder
from app.common.constants import KINESIS_DEFAULT_FAILURE_DIR
from app.common.constants import KINESIS_DEFAULT_FAILURE_MAX_FILE_SIZE_MB


class IFailureHandler(abc.ABC):
    @abstractmethod
    def handle_failure(self, locations: list[DriverLocation]):
        pass


class SqsQueueFailureHandler(IFailureHandler):
    def __init__(self, queue_url, failure_dir=KINESIS_DEFAULT_FAILURE_DIR):
        if not queue_url:
            raise Exception('queue_url must not be empty')
        self._queue_url = queue_url
        self._sqs = boto3.client('sqs')
        self._file_handler = FileFailureHandler(failure_dir)

    """
    When location records cannot be sent to Kinesis, the locations
    will be sent to an SQS queue.
    """
    def handle_failure(self, locations: list[DriverLocation]):
        msg = json.dumps(locations, cls=DriverLocationJsonEncoder)
        try:
            response = self._sqs.send_message(
                QueueUrl=self._queue_url,
                MessageBody=msg)
            log.info(f"{len(locations)} locations sent to queue - MessageId: {response['MessageId']}")
        except botocore.exceptions.ClientError as c_ex:
            log.info(f"Could not send records to queue: {c_ex}")
            self._file_handler.handle_failure(locations)
            log.debug(c_ex)


class DynamoDbFailureHandler(IFailureHandler):
    def __init__(self, table_name, failure_dir=KINESIS_DEFAULT_FAILURE_DIR):
        self._table_name = table_name
        self._dynamodb = boto3.client('dynamodb')
        self._file_handler = FileFailureHandler(failure_dir)
        pass

    def handle_failure(self, locations: list[DriverLocation]):
        try:
            locations_str = json.dumps(locations, cls=DriverLocationJsonEncoder)
            self._dynamodb.put_item(
                TableName=self._table_name,
                Item={
                    "Timestamp": datetime.now().isoformat(),
                    "Locations": locations_str
                })
        except botocore.exceptions.ClientError as c_ex:
            self._file_handler.handle_failure(locations)
            log.debug(c_ex)


class FileFailureHandler(IFailureHandler):
    """
    When location records cannot be sent to Kinesis, the locations
    will be stored in a JSON file in the directory passed to the
    constructor.
    """
    def __init__(self, directory, max_file_size_mb=KINESIS_DEFAULT_FAILURE_MAX_FILE_SIZE_MB):
        self._directory = pathlib.Path(directory).resolve()
        Path(self._directory).mkdir(parents=True, exist_ok=True)
        self._max_file_size_mb = max_file_size_mb

    def handle_failure(self, locations: list[DriverLocation]):
        file_name = self._get_latest_file_path()
        with open(file_name, 'a') as file:
            json.dump(locations, file, cls=DriverLocationJsonEncoder)
            file.write(os.linesep)
        log.info(f"{len(locations)} locations appended to file {file_name}")

    def _get_latest_file_path(self):
        today = date.today()
        today_dir = f"{self._directory}/{today}"
        if not os.path.isdir(today_dir):
            log.debug(f"Dir does not exist. Creating directory {today_dir}")
            Path(today_dir).mkdir(parents=True, exist_ok=True)
            return f"{today_dir}/1"
        else:
            file = "1"
            for f in os.listdir(today_dir):
                if int(f) > int(file):
                    file = f
            if os.path.getsize(f"{today_dir}/{file}") > (self._max_file_size_mb * 1024 * 1024):
                return f"{today_dir}/{int(file) + 1}"
            else:
                return f"{today_dir}/{file}"


class NoopFailureHandler(IFailureHandler):
    def handle_failure(self, locations: list[DriverLocation]):
        log.info(f"Nothing done with {len(locations)} locations.")
