from abc import ABCMeta
import httpx
import json

random_quote_url = "https://api.quotable.io/random"


class DBInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "save_quote") and callable(subclass.save_quote)


class Quote:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Service:
    def __init__(self, db: DBInterface):
        self.db = db

    def get_random_quote(self):
        r = httpx.get(random_quote_url)
        random_quote = json.loads(r.text)
        quote = Quote(
            id=random_quote["_id"],
            quote=random_quote["content"],
            author=random_quote["author"],
            tags=random_quote["tags"],
            likes=0,
        )
        self.db.save_quote(quote)
        return quote
