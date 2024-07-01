from abc import ABCMeta
from src.config.config import QuotesConfig
import random


class DBInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_quote")
            and callable(subclass.get_quote)
            and hasattr(subclass, "get_quotes")
            and callable(subclass.get_quotes)
            and hasattr(subclass, "get_same_quote")
            and callable(subclass.get_same_quote)
            and hasattr(subclass, "get_view")
            and callable(subclass.get_view)
            and hasattr(subclass, "mark_as_viewed")
            and callable(subclass.mark_as_viewed)
            and hasattr(subclass, "mark_as_liked")
            and callable(subclass.mark_as_liked)
            and hasattr(subclass, "like_quote")
            and callable(subclass.like_quote)
        )


class APIInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "get_random_quote") and callable(
            subclass.get_random_quote
        )


class Quote:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Service:
    def __init__(self, cfg: QuotesConfig, db: DBInterface, api: APIInterface):
        self.cfg = cfg
        self.db = db
        self.api = api

    def get_quote(self, user_id: str):
        quotes = self.db.get_quotes(user_id)
        quote = self.__getQuote(quotes)
        self.db.mark_as_viewed(quote.id, user_id)
        return Quote(
            id=quote.id,
            quote=quote.quote,
            author=quote.author,
            tags=quote.tags,
            likes=quote.likes,
        )

    def like_quote(self, user_id: str, quote_id: str):
        view = self.db.get_view(quote_id, user_id)
        if view.liked:
            return
        self.db.like_quote(quote_id)
        self.db.mark_as_liked(quote_id, user_id)

    def get_same_quote(self, user_id: str, quote_id: str):
        viewed_quote = self.db.get_quote(quote_id)
        quote = self.db.get_same_quote(user_id, viewed_quote)
        if quote is None:
            quote = self.api.get_random_quote()
        self.db.mark_as_viewed(quote.id, user_id)
        return Quote(
            id=quote.id,
            quote=quote.quote,
            author=quote.author,
            tags=quote.tags,
            likes=quote.likes,
        )

    def __getQuote(self, quotes=[]):
        random_percent = random.uniform(0.0, 100.0)
        if (100.0 - self.cfg.random_quote_chance) > random_percent and len(quotes) > 0:
            likes: float = 0.0
            for quote in quotes:
                if quote.likes == 0:
                    quote.likes += 1

                likes += quote.likes

            accumulator: float = 0.0
            delimiter: float = likes * 100.0 / (100.0 - self.cfg.random_quote_chance)
            for i, quote in enumerate(quotes):
                if quote.likes == 0:
                    quote.likes += 1

                percent = quote.likes / delimiter * 100.0
                if percent + accumulator >= random_percent:
                    return quotes[i]

                accumulator += percent

        return self.api.get_random_quote()
