import sys
import time
import json
import boto3
import argparse
import logging as log
import botocore.exceptions

from app.config import Config
from app.consume.kinesis.streamer import KinesisStreamer
from app.consume.kinesis.failure import NoopFailureHandler
from app.common.constants import KINESIS_DEFAULT_STREAM_NAME
from app.common.json_encoder import DriverLocationJsonDecoder


class RetryArgParser:
    def __init__(self, args):
        self.parser = argparse.ArgumentParser(prog='app.consume.kinesis.retry', description='Continuous service to retry stream failures')
        self.parser.add_argument('-d', '--delay', type=int, default=5, help='delay (seconds) to poll queue')
        self.parser.add_argument('-w', '--wait-time', type=int, default=20, help='wait time for queue long polling (0-20)')
        self.parser.add_argument('-m', '--max-messages', type=int, default=10, help='max sqs messages for receive request')
        self.parser.add_argument('-n', '--stream-name', type=str, default=KINESIS_DEFAULT_STREAM_NAME,
                                 help='name of the Kinesis stream')
        self.parser.add_argument('-l', '--log', choices=['INFO', 'DEBUG', 'WARN', 'ERROR'], default=log.INFO,
                                 help='log level (INFO, DEBUG, WARN, ERROR')
        self._args = self.parser.parse_args(args)

    def get_args(self):
        return self._args


def get_messages(sqs, queue_url, wait_time, max_messages):
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            WaitTimeSeconds=wait_time,
            MaxNumberOfMessages=max_messages)
        log.debug(response)
        if 'Messages' in response:
            messages = response['Messages']
            log.info(f"{len(messages)} retrieved.")
            return messages
        else:
            log.info("No messages retrieved.")
            return None
    except botocore.exceptions.ClientError as c_ex:
        log.info(f"Could not get messages: {c_ex}")
        log.debug(c_ex)


def delete_message(sqs, queue_url, receipt_handle):
    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle)
        log.info(f"Message {receipt_handle} deleted")
    except botocore.exceptions.ClientError as c_ex:
        log.info(f"Cloud not delete receipt handle: {receipt_handle}")
        log.debug(c_ex)


def stream_message(kinesis, stream_name, message) -> bool:
    locations = json.loads(message['Body'], cls=DriverLocationJsonDecoder)
    response = KinesisStreamer.send_locations(kinesis=kinesis, stream_name=stream_name, locations=locations,
                                              failure_handler=NoopFailureHandler())
    if response.get_status() == KinesisStreamer.Response.Status.SUCCESS:
        return True
    else:
        return False


def main(_args):
    args = RetryArgParser(_args).get_args()
    log.basicConfig(level=args.log)

    config = Config()
    if config.failover_queue_url is None:
        log.error('FAILOVER_QUEUE_URL is not set.')
        sys.exit(1)

    sqs = boto3.client('sqs')
    kinesis = boto3.client('kinesis')
    stream_name = args.stream_name
    queue_url = config.failover_queue_url
    while True:
        log.info(f"Fetching messages...")
        messages = get_messages(sqs, queue_url, args.wait_time, args.max_messages)
        if messages is not None:
            for message in messages:
                log.debug(message)
                if stream_message(kinesis, stream_name, message):
                    delete_message(sqs=sqs, queue_url=queue_url, receipt_handle=message['ReceiptHandle'])
        time.sleep(args.delay)


if __name__ == '__main__':
    main(sys.argv[1:])
