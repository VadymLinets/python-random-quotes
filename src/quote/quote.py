import random

from src.config.config import QuotesConfig
from src.quote.interfaces import DBInterface, APIInterface, Quote

ONE_HUNDRED_PERCENT: float = 100.0


class Service:
    def __init__(self, cfg: QuotesConfig, db: DBInterface, api: APIInterface):
        self.cfg = cfg
        self.db = db
        self.api = api

    def get_quote(self, user_id: str) -> Quote:
        quotes = self.db.get_quotes(user_id)
        quote = self.choose_quote(quotes, random.uniform(0.0, ONE_HUNDRED_PERCENT))
        self.db.mark_as_viewed(quote.id, user_id)
        return Quote(
            id=quote.id,
            quote=quote.quote,
            author=quote.author,
            tags=quote.tags,
            likes=quote.likes,
        )

    def like_quote(self, user_id: str, quote_id: str) -> None:
        view = self.db.get_view(quote_id, user_id)
        if view is None or view.liked:
            return
        self.db.like_quote(quote_id)
        self.db.mark_as_liked(quote_id, user_id)

    def get_same_quote(self, user_id: str, quote_id: str) -> Quote:
        viewed_quote = self.db.get_quote(quote_id)
        if viewed_quote is not None:
            quote = self.db.get_same_quote(user_id, viewed_quote)
            if quote is None:
                quote = self.api.get_random_quote()
        else:
            quote = self.api.get_random_quote()
        self.db.mark_as_viewed(quote.id, user_id)
        return Quote(
            id=quote.id,
            quote=quote.quote,
            author=quote.author,
            tags=quote.tags,
            likes=quote.likes,
        )

    def choose_quote(
        self, quotes: list[Quote], random_percent: float = 0.0
    ) -> Quote:
        if (ONE_HUNDRED_PERCENT - self.cfg.random_quote_chance) > random_percent and len(quotes) > 0:
            likes: float = 0.0
            for quote in quotes:
                likes += quote.likes if quote.likes > 0 else 1

            accumulator: float = 0.0
            delimiter: float = likes * ONE_HUNDRED_PERCENT / (ONE_HUNDRED_PERCENT - self.cfg.random_quote_chance)
            for quote in quotes:
                likes = quote.likes if quote.likes > 0 else 1
                percent = likes / delimiter * ONE_HUNDRED_PERCENT
                if percent + accumulator >= random_percent:
                    return quote

                accumulator += percent

        return self.api.get_random_quote()
