
from app.produce.geo import Geo, TravelPlan
from tests.produce.common import _get_drivers_list


def test_geo_get_points_from_file(monkeypatch):
    monkeypatch.setattr('app.produce.geo.DEFAULT_POINTS_DIR', 'tests/files')
    driver = _get_drivers_list()[0]

    geo = Geo()
    plan: TravelPlan = geo.get_points(driver, driver.deliveries[0])

    assert plan.distance == 65
    assert len(plan.points) == 10
