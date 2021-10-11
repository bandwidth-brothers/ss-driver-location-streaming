from app.config import Config
from app.db.database import Database
from app.data.dbdata import DataGenerator


db = Database(Config())


def _get_row_count(table):
    return db.run_query(f'SELECT COUNT(id) FROM `{table}`')[0][0]


def test_data_generator_generate_restaurants():
    generator = DataGenerator()
    generator.delete_all()
    generator.generate_restaurants()

    rest_count = _get_row_count('restaurant')
    assert rest_count == 37

    addr_count = _get_row_count('address')
    assert addr_count == 37

    generator.delete_all()


def test_data_generator_generate_customers():
    generator = DataGenerator()
    generator.delete_all()

    generator.generate_customers(2)

    cust_count = _get_row_count('customer')
    assert cust_count == 2
    user_count = _get_row_count('user')
    assert user_count == 2
    addr_count = _get_row_count('address')
    assert addr_count == 2

    generator.delete_all()


def test_data_generator_generate_drivers():
    generator = DataGenerator()
    generator.delete_all()

    generator.generate_drivers(2)

    cust_count = _get_row_count('driver')
    assert cust_count == 2
    user_count = _get_row_count('user')
    assert user_count == 2
    addr_count = _get_row_count('address')
    assert addr_count == 2

    generator.delete_all()


def test_data_generator_generate_orders():
    generator = DataGenerator()
    generator.delete_all()

    generator.generate_restaurants()
    generator.generate_drivers(1)
    generator.generate_customers(2)
    generator.generate_orders(2)

    order_count = _get_row_count('order')
    assert order_count == 2

    generator.delete_all()


def test_data_generator_generate_deliveries():
    generator = DataGenerator()
    generator.delete_all()

    generator.generate_restaurants()
    generator.generate_drivers(1)
    generator.generate_customers(2)
    generator.generate_orders(2)
    generator.generate_deliveries()

    deliv_count = _get_row_count('delivery')
    assert deliv_count == 2

    generator.delete_all()
