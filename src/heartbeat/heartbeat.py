from abc import ABCMeta


class DBInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "ping") and callable(subclass.ping)

class Service:
    def __init__(self, db: DBInterface):
        self.db = db

    def ping_database(self):
        self.db.ping()