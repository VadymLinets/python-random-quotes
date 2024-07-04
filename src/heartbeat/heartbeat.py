from src.heartbeat.interfaces import DBInterface


class Service:
    def __init__(self, db: DBInterface):
        self.db = db

    def ping_database(self) -> None:
        self.db.ping()
