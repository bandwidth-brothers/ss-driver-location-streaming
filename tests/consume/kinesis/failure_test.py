import os
import json
import shutil

from datetime import date
from datetime import datetime
from app.produce.domain import DriverLocation
from app.consume.kinesis.failure import FileFailureHandler


def _assert_location(location_data, expected_location: DriverLocation):
    assert expected_location.driver_id == location_data['driver_id']
    assert expected_location.delivery_id == location_data['delivery_id']
    assert expected_location.lat == location_data['lat']
    assert expected_location.lng == location_data['lng']


TEST_DIR = "./tmp/tests/kinesis/failure"


def test_file_failure_handler_handle_failure_data_saved():
    locations = [
        DriverLocation(1, 2, '38.95468295847049', '-76.9926861397328', datetime.now()),
        DriverLocation(3, 4, '38.90251113257459', '-77.0115738467624', datetime.now()),
        DriverLocation(5, 5, '38.95450307540628', '-77.0115611403354', datetime.now())]

    FileFailureHandler(directory=TEST_DIR).handle_failure(locations)

    directory = f"{TEST_DIR}/{date.today()}"
    file = [f for f in os.listdir(directory)][0]
    with open(f"{directory}/{file}") as f:
        data = json.loads(f.readline())

    _assert_location(data[0], locations[0])
    _assert_location(data[1], locations[1])
    _assert_location(data[2], locations[2])

    shutil.rmtree(TEST_DIR)


def test_file_failure_handler_handle_failure_new_file_created_after_max_size():
    locations = [
        DriverLocation(1, 2, '38.95468295847049', '-76.9926861397328', datetime.now()),
        DriverLocation(3, 4, '38.90251113257459', '-77.0115738467624', datetime.now()),
        DriverLocation(5, 5, '38.95450307540628', '-77.0115611403354', datetime.now())]

    handler = FileFailureHandler(directory=TEST_DIR, max_file_size_mb=1)
    for _ in range(10000):
        handler.handle_failure(locations)

    today = date.today()
    failure_dir = f"{TEST_DIR}/{today}"
    assert len(os.listdir(failure_dir)) == 4

    shutil.rmtree(TEST_DIR)
