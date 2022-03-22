import re
import logging as log

from app.produce.main import main
from tests.produce.common import _get_drivers_list


def test_producer_main(monkeypatch, caplog):
    monkeypatch.setattr('app.produce.producer.Deliveries.get_driver_deliveries', _get_drivers_list)
    monkeypatch.setattr('app.produce.producer.Deliveries.set_delivery_picked_up_at', lambda a, b: None)
    caplog.set_level(log.INFO)

    main(['--log', 'INFO', '--no-api-key', '--data-dir', 'tests/files'])

    records = list(filter(lambda rec: re.match(".*[0-9]$", rec.message), caplog.records))
    points = map(lambda rec: int(rec.message.split()[-1]), records)
    expected = [10, 11, 7, 28]
    for point in points:
        assert point in expected
