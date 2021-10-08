from functools import reduce
from app.data.dbdata import DataGenerator
from app.data.deliveries import Deliveries


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
