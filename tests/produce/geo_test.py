import pytest

from os import environ
from app.produce.geo import Geo, TravelPlan
from tests.produce.common import _get_drivers_list


def test_geo_get_points_from_file(monkeypatch):
    monkeypatch.setattr('app.produce.geo.GEO_DEFAULT_POINTS_DIR', 'tests/files')
    driver = _get_drivers_list()[0]

    geo = Geo(no_api_key=True)
    plan: TravelPlan = geo.get_points(driver, driver.deliveries[0])

    assert plan.distance == 65
    assert len(plan.points) == 10


def test_geo_exit_when_no_api_key(caplog):
    Geo(no_api_key=True)

    log_msg = caplog.records[0].message
    assert 'Will not be able to make API calls' in log_msg


def test_geo_exit_when_no_api_key_environment_variable(caplog):
    environ.pop('GOOGLE_API_KEY')
    with pytest.raises(SystemExit):
        Geo()

    log_msg = caplog.records[0].message
    assert 'GOOGLE_API_KEY environment variable not set' in log_msg


def test_geo_with_bad_api_key(caplog):
    environ['GOOGLE_API_KEY'] = "InvalidKey"
    with pytest.raises(SystemExit):
        Geo()

    log_msg = caplog.records[0].message
    assert 'Invalid API key' in log_msg
