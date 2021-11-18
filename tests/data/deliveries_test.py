from datetime import datetime
from functools import reduce
from app.config import Config
from app.db.database import Database
from app.data.dbdata import DataGenerator
from app.produce.domain import Delivery
from app.data.deliveries import Deliveries


db = Database(Config())


def test_deliveries_get_driver_deliveries():
    generator = DataGenerator()
    generator.delete_all()
    generator.generate_restaurants()
    generator.generate_drivers(2)
    generator.generate_customers(4)
    generator.generate_orders(4)
    generator.generate_deliveries()

    drivers = Deliveries.get_driver_deliveries()
    assert len(drivers) == 2

    deliv_count = reduce(lambda count, driver: count + len(driver.deliveries), drivers, 0)
    assert deliv_count == 4

    generator.delete_all()


def test_set_delivery_picked_up_at():
    generator = DataGenerator()
    generator.delete_all()
    generator.generate_restaurants()
    generator.generate_drivers(1)
    generator.generate_customers(1)
    generator.generate_orders(1)
    generator.generate_deliveries()

    result = db.run_query('SELECT id, picked_up_at FROM delivery LIMIT 1')[0]
    assert result[1] is None

    timestamp = datetime.now()
    Deliveries.set_delivery_picked_up_at(delivery_id=result[0], timestamp=timestamp)

    result = db.run_query('SELECT id, picked_up_at FROM delivery LIMIT 1')[0]
    db_timestamp = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S.%f")
    assert db_timestamp.replace(microsecond=0) == timestamp.replace(microsecond=0)
