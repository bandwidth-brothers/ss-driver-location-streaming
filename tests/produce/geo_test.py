import os
import shutil

import pytest
import googlemaps

from os import environ
from shutil import copyfile
from app.produce.geo import GoogleMapsGeo, TravelPlan
from tests.produce.common import _get_drivers_list


def test_google_maps_geo_get_points_from_file():
    driver = _get_drivers_list()[0]

    geo = GoogleMapsGeo(no_api_key=True, data_dir='tests/files')
    plan: TravelPlan = geo.get_points(driver, driver.deliveries[0])

    assert plan.distance == 65
    assert len(plan.points) == 10


def test_google_maps_geo_return_when_no_api_key(caplog):
    if os.getenv('GOOGLE_API_KEY'):
        environ.pop('GOOGLE_API_KEY')
    geo = GoogleMapsGeo(no_api_key=True)

    log_msg = caplog.records[0].message
    assert 'Will not be able to make API calls' in log_msg
    assert hasattr(geo, 'gmaps') is False


def test_google_maps_geo_exit_when_no_api_key_environment_variable(caplog):
    with pytest.raises(SystemExit):
        GoogleMapsGeo()

    log_msg = caplog.records[0].message
    assert 'GOOGLE_API_KEY environment variable not set' in log_msg


def test_google_maps_geo_with_bad_api_key(caplog):
    environ['GOOGLE_API_KEY'] = "InvalidKey"
    with pytest.raises(SystemExit):
        GoogleMapsGeo()

    log_msg = caplog.records[0].message
    assert 'Invalid API key' in log_msg


def test_google_maps_geo_make_maps(func_args):
    os.makedirs('tmp/tests/geo/points', exist_ok=True)
    os.makedirs('tmp/tests/geo/maps', exist_ok=True)
    copyfile('tests/files/points/1-1-points.txt', 'tmp/tests/geo/points/1-1-.points.txt')

    geo = GoogleMapsGeo(no_api_key=True, data_dir='tmp/tests/geo')
    geo.gmaps = googlemaps.Client
    og_static_map = googlemaps.Client
    geo.gmaps.static_map = func_args

    geo.make_maps()
    assert os.path.exists('tmp/tests/geo/maps/1-1-map.png')

    kwargs = func_args.get_kwargs()
    center_marker = kwargs['center']
    assert center_marker == ('38.954233250796946', '-77.01154208081533')

    markers = kwargs['markers']
    # see StaticMapMarker source code
    locations = markers[0].params[2].split('|')
    assert len(locations) == 10

    shutil.rmtree('tmp/tests/geo')
    googlemaps.Client.static_map = og_static_map
