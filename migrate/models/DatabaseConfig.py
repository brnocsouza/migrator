class DatabaseConfig:
    host: str = None
    port: int = None
    uri: str = None
    database: str = None
    user: str = None
    password: str = None

    def __getitem__(self, item):
        return self[item]


class MongoDBConfig(DatabaseConfig):
    authSource: str = None,
    authMechanism: str = 'SCRAM-SHA-1'
