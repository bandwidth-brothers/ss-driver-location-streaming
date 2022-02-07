import time
import boto3
import logging as log

from app.produce.geo import RandomGeo
from app.produce.geo import GoogleMapsGeo
from app.common.constants import KINESIS_DEFAULT_DELAY
from app.common.constants import KINESIS_DEFAULT_STREAM_NAME
from app.common.constants import KINESIS_DEFAULT_RECORDS_PER_REQUEST
from app.common.constants import PRODUCER_DEFAULT_DELAY
from app.produce.producer import DriverLocationProducer
from app.produce.producer import PRODUCER_DEFAULT_MAX_THREADS
from app.produce.producer import PRODUCER_DEFAULT_BUFFER_SIZE
from app.consume.kinesis.failure import IFailureHandler
from app.consume.kinesis.streamer import KinesisStreamer


class KinesisDriverLocationConsumer:

    def __init__(self,
                 stream_name=KINESIS_DEFAULT_STREAM_NAME,
                 records_per_request=KINESIS_DEFAULT_RECORDS_PER_REQUEST,
                 delay=KINESIS_DEFAULT_DELAY,
                 producer_max_threads=PRODUCER_DEFAULT_MAX_THREADS,
                 producer_buffer_size=PRODUCER_DEFAULT_BUFFER_SIZE,
                 producer_delay=PRODUCER_DEFAULT_DELAY,
                 producer_no_api_key=False,
                 producer_no_gapi=False,
                 failure_handler: IFailureHandler = None):
        self._kinesis = boto3.client('kinesis')
        self._delay = delay
        self._stream_name = stream_name
        self._records_per_request = records_per_request
        self._failure_handler = failure_handler

        if producer_no_gapi:
            geo = RandomGeo()
        else:
            geo = GoogleMapsGeo(no_api_key=producer_no_api_key)

        self._producer = DriverLocationProducer(geo=geo,
                                                buffer_size=producer_buffer_size,
                                                max_threads=producer_max_threads,
                                                delay=producer_delay)

    def stream_locations_to_kinesis(self):
        self._producer.start()
        self._producer.join()

        success_count = 0
        failed_count = 0
        total_locations = 0
        locations = []

        def _increment_counts(_response: KinesisStreamer.Response):
            nonlocal success_count
            nonlocal failed_count
            if _response.Status == KinesisStreamer.Response.Status.SUCCESS:
                success_count += _response.get_num_records()
            else:
                failed_count += _response.get_num_records()

        for location in self._producer.get_driver_locations():
            locations.append(location)
            total_locations += 1
            if len(locations) == self._records_per_request:
                response = KinesisStreamer.send_locations(self._kinesis, self._stream_name, locations, self._failure_handler)
                _increment_counts(response)
                locations.clear()
                time.sleep(self._delay)
        # send remaining locations
        if locations:
            result = KinesisStreamer.send_locations(self._kinesis, self._stream_name, locations, self._failure_handler)
            _increment_counts(result)

        log.info(f"Total Records Success: {success_count}")
        log.info(f"Total Records Failed: {failed_count}")
        log.info(f"Total Locations: {total_locations}")
