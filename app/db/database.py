import sys

import jaydebeapi
import logging as log


class Database:

    def __init__(self, config):
        self.db_url = config.db_url
        self.db_user = config.db_user
        self.db_password = config.db_password
        self.db_driver = config.db_driver
        self.db_jarfile = config.db_jarfile
        self.conn = None

    def open_connection(self):
        try:
            if self.conn is None:
                self.conn = jaydebeapi.connect(
                    self.db_driver,
                    self.db_url,
                    {'user': self.db_user, 'password': self.db_password},
                    self.db_jarfile
                )
        except jaydebeapi.DatabaseError as e:
            print('Could not connect to the database. '
                  'Check environment variables and database accessibility.')
            log.error(e)
            sys.exit(1)
        finally:
            log.debug('Connection opened successfully.')

    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            log.debug('Database connection closed.')

    def run_query(self, query):
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                records = []
                cur.execute(query)
                result = cur.fetchall()
                for row in result:
                    records.append(row)
                cur.close()
                return records
        except jaydebeapi.DatabaseError as e:
            log.error(e)
            raise e
        finally:
            self.close_connection()

    def update(self, query, args):
        try:
            self.open_connection()
            with self.conn.cursor() as cur:
                cur.execute(query, args)
        except jaydebeapi.DatabaseError as e:
            log.error(e)
            raise e
        finally:
            self.close_connection()
