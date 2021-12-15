from os import environ
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv(environ.get('ENV_FILE') or '.env')
        self.api_key = environ.get('GOOGLE_API_KEY')
        self.db_user = environ.get('DATABASE_USERNAME')
        self.db_password = environ.get('DATABASE_PASSWORD')
        self.db_url = environ.get('DATABASE_URL')
        self.db_driver = environ.get('DATABASE_DRIVER')
        self.db_jarfile = environ.get('DATABASE_JARFILE')
        self.failover_queue_url = environ.get('FAILOVER_QUEUE_URL')
