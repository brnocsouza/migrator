from abc import ABC, abstractmethod

from migrate.models import DatabaseConfig


class BaseDBClient(ABC):
    def __init__(self, database: DatabaseConfig):
        self.host = database['host']
        self.user = database['user']
        self.password = database['password']
        self.port = database['port']
        self.uri = database['uri']
        self.client = None

    @abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError()

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()
