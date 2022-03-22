import argparse

from argparse import RawTextHelpFormatter
from rich.console import Console, Control
from app.data.dbdata import DataGenerator


class DataArgParser:
    def __init__(self, args):
        self._parser = argparse.ArgumentParser(prog='app.data', formatter_class=RawTextHelpFormatter,
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

    python -m app.data --drivers 4 --custs 10  --orders 10
    python -m app.data --delete-all""")

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
    console = Console()

    if args.delete_all:
        with console.status("[bold green]Deleting records..."):
            generator.delete_all()
        console.print("All records deleted!", style='bold yellow')
        return

    def _generate_records(gen_func, count, msg):
        console.print(f"{msg}...",  style='white')
        if count is not None:
            gen_func(count)
        else:
            gen_func()
        console.control(Control.move(0, -1))
        console.print(f"{msg} :heavy_check_mark:", style='bold green')

    with console.status("[bold green]Creating records..."):
        _generate_records(generator.generate_restaurants, None, "Creating restaurants")
        _generate_records(generator.generate_drivers, args.drivers, "Creating drivers")
        _generate_records(generator.generate_customers, args.custs, "Creating customers")
        _generate_records(generator.generate_orders, args.orders, "Creating orders")
        _generate_records(generator.generate_deliveries, None, "Creating deliveries")
        console.print('[bold yellow]Done!')
