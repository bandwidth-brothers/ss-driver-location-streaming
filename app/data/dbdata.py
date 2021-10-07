import csv
import json
import sys
import uuid
import random
import argparse

from argparse import RawTextHelpFormatter
from app.config import Config
from app.db.database import Database
from app.data.users import User
from app.data.users import UserGenerator


class DataGenerator:
    def __init__(self):
        self.db = Database(Config())
        self.names = self._load_names()
        self.addresses = self._load_addresses()

    @staticmethod
    def _load_names():
        names = []
        with open('data/names.txt') as f:
            for line in f:
                fields = line.split()
                names.append({'first': fields[0].strip(), 'last': fields[1].strip()})
        return names

    @staticmethod
    def _load_addresses():
        with open('data/addresses-dc.json') as f:
            addresses = json.load(f)
        return addresses

    def delete_all(self):
        tables = ['delivery', 'order', 'restaurant', 'owner', 'driver', 'customer', 'address', 'user']
        self.db.open_connection()
        self.db.conn.jconn.setAutoCommit(False)
        with self.db.conn.cursor() as curs:
            for table in tables:
                curs.execute(f"DELETE FROM `{table}`")
        self.db.conn.commit()
        self.db.close_connection()

    def generate_customers(self, count: int):
        if count < 1:
            return

        self.db.open_connection()
        self.db.conn.jconn.setAutoCommit(False)
        with self.db.conn.cursor() as curs:
            for i in range(count):
                user_id = self._create_user(curs, User.Role.CUSTOMER)
                address_id = self._create_address(curs, self.addresses[i])
                curs.execute('INSERT INTO customer (id, address_id, first_name, last_name, phone, loyalty_points) '
                             'VALUES(UNHEX(?), ?, ?, ?, ?, ?)',
                             (user_id.hex, address_id, self.names[i]['first'], self.names[i]['last'], '202-555-1234', 10))
        self.db.conn.commit()
        self.db.close_connection()

    def generate_restaurants(self):
        with open('data/restaurants-dc.csv') as f:
            count = 0
            current_restaurant = ""

            self.db.open_connection()
            self.db.conn.jconn.setAutoCommit(False)
            with self.db.conn.cursor() as curs:
                for restaurant in csv.DictReader(f):
                    if restaurant['name'] != current_restaurant:
                        current_restaurant = restaurant['name']
                        owner_id = self._create_owner(curs, random.choice(self.names))
                    address_id = self._create_address(curs, restaurant)
                    curs.execute('INSERT INTO restaurant (address_id, owner_id, name, rating) '
                                 'VALUES (?, UNHEX(?), ?, ?)',
                                 (address_id, owner_id.hex, restaurant['name'], 5))
                    count += 1
            self.db.conn.commit()
            self.db.close_connection()

    def generate_orders(self, count):
        if count < 1:
            return

        self.db.open_connection()
        self.db.conn.jconn.setAutoCommit(False)
        with self.db.conn.cursor() as curs:
            restaurant_ids = self._get_restaurant_ids(curs)
            customer_ids = self._get_customer_ids(curs)

            for i in range(count):
                if i >= len(customer_ids) - 1:
                    customer_id = random.choice(customer_ids)
                else:
                    customer_id = customer_ids[i]
                curs.execute('INSERT INTO `order` (restaurant_id, customer_id) VALUES (?, UNHEX(?))',
                             (random.choice(restaurant_ids), customer_id))
        self.db.conn.commit()
        self.db.close_connection()

    def generate_drivers(self, count):
        if count < 1:
            return

        addresses = list(reversed(self.addresses))
        names = list(reversed(self.names))

        self.db.open_connection()
        self.db.conn.jconn.setAutoCommit(False)
        with self.db.conn.cursor() as curs:
            for i in range(count):
                address_id = self._create_address(curs, addresses[i])
                driver_id = self._create_user(curs, User.Role.DRIVER)
                license_num = uuid.uuid4().hex.replace('-', '')[0:10]
                name = names[i]
                curs.execute('INSERT INTO driver (id, address_id, first_name, last_name, phone, license_num, status) '
                             'VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?)',
                             (driver_id.hex, address_id, name['first'], name['last'], '202-555-1234', license_num, 'ACTIVE'))
        self.db.conn.commit()
        self.db.close_connection()

    def generate_deliveries(self):
        self.db.open_connection()
        self.db.conn.jconn.setAutoCommit(False)
        with self.db.conn.cursor() as curs:
            order_ids = self._get_order_ids(curs)
            driver_ids = self._get_driver_ids(curs)

            for order_id in order_ids:
                address_id = self._get_address_id_by_order_id(curs, order_id)
                driver_id = random.choice(driver_ids)
                curs.execute('INSERT INTO delivery (address_id, driver_id, order_id) '
                             'VALUES (?, UNHEX(?), ?)',
                             (address_id, driver_id, order_id))
        self.db.conn.commit()
        self.db.close_connection()

    def _create_user(self, curs, user_role: str) -> uuid.UUID:
        user = UserGenerator.generate_user(user_role)
        curs.execute('INSERT INTO user (id, user_role, password, email, enabled, confirmed, account_non_expired, '
                     '                  account_non_locked, credentials_non_expired) '
                     'VALUES (UNHEX(?), ?, ?, ?, ?, ?, ?, ?, ?)',
                     (user.id.hex, user.user_role, user.password, user.email, user.enabled, user.confirmed,
                      user.account_non_expired, user.account_non_locked, user.credentials_non_expired))
        return user.id

    def _create_owner(self, curs, name) -> uuid.UUID:
        owner_id = self._create_user(curs, User.Role.EMPLOYEE)
        curs.execute('INSERT INTO owner (id, first_name, last_name) VALUES (UNHEX(?), ?, ?)',
                     (owner_id.hex, name['first'], name['last']))
        return owner_id

    def _create_address(self, curs, address) -> int:
        curs.execute('INSERT INTO address (line1, city, state, zip) VALUES (?, ?, ?, ?)',
                     (address['address1'], address['city'], address['state'], address['postalCode']))
        return self._get_last_insert_id(curs, 'address')

    def _get_last_insert_id(self, curs, table: str):
        curs.execute(f"SELECT MAX(id) FROM `{table}`")
        last_id = curs.fetchone()[0]
        return last_id if last_id is not None else 1

    def _get_ids(self, curs, query, transform=lambda res: res):
        curs.execute(query)
        results = curs.fetchall()
        return list(map(lambda result: transform(result[0]), results))

    def _get_owner_ids(self, curs):
        return self._get_ids(curs, 'SELECT HEX(id) FROM owner')

    def _get_restaurant_ids(self, curs):
        return self._get_ids(curs, 'SELECT id FROM restaurant')

    def _get_customer_ids(self, curs):
        return self._get_ids(curs, 'SELECT HEX(id) FROM customer')

    def _get_order_ids(self, curs):
        return self._get_ids(curs, 'SELECT id FROM `order`')

    def _get_driver_ids(self, curs):
        return self._get_ids(curs, 'SELECT HEX(id) FROM driver')

    def _get_address_id_by_order_id(self, curs, order_id):
        curs.execute('SELECT c.address_id FROM `order` o '
                     'JOIN customer c ON o.customer_id = c.id '
                     f"WHERE o.id = {order_id}")
        return curs.fetchone()[0]


class DataArgParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                               description="""Generate delivery data an dependency data.

Deliveries require that there be an Order. and Orders require that there
be Restaurants, Customers, and Drivers in the database. This program can
produce this required data.

Restaurants will be automatically created. When an Order is created, a
random Restaurant and Customer will be chosen. A Delivery will be created
for each Order. Drivers will be chosen randomly for each Order/Delivery.
A Driver may end up with multiple Deliveries.

All data can be deleted with the --delete-all/-d flag. All data will be
delete from the following tables:
    delivery, order, restaurant, owner, driver, customer, address, user

examples:

    python -m app.data.dbdata --drivers 4 --custs 10  --orders 10
    python -m app.data.dbdata --delete-all""")

        self._parser.add_argument('--drivers', type=int, default=0, help='number of drivers to create')
        self._parser.add_argument('--custs', type=int, default=0, help='number of customers to create')
        self._parser.add_argument('--orders', type=int, default=0, help='number of orders to create')
        self._parser.add_argument('--delete-all', '-d', action='store_true', help='delete all data')
        self._args = self._parser.parse_args(args)

    def get_args(self):
        return self._args


def main(_args):
    parser = DataArgParser(_args)
    args = parser.get_args()
    generator = DataGenerator()

    if args.delete_all:
        generator.delete_all()
        return

    generator.generate_restaurants()
    generator.generate_drivers(args.drivers)
    generator.generate_customers(args.custs)
    generator.generate_orders(args.orders)
    generator.generate_deliveries()


if __name__ == '__main__':
    main(sys.argv[1:])
