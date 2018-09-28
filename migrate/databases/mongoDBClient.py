from pymongo import MongoClient

from migrate.databases.BaseDBClient import BaseDBClient
from migrate.models.DatabaseConfig import MongoDBConfig


class MongoDBClient(BaseDBClient):

    def __init__(self, database: MongoDBConfig):
        super().__init__(database)
        self.authSource = database['authSource']
        self.authMechanism = database['authMechanism']

    def close(self):
        self.client.close()

    def connect(self):
        if self.uri is not None:
            self.client = MongoClient(self.uri)
        else:
            self.client = MongoClient(self.uri)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        self.connect()
