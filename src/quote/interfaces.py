from abc import ABC, abstractmethod

from src.quote.models import Quote, View


class DBInterface(ABC):
    @abstractmethod
    def get_quote(self, quote_id: str) -> Quote:
        pass

    @abstractmethod
    def get_quotes(self, user_id: str) -> list[Quote]:
        pass

    @abstractmethod
    def get_same_quote(self, user_id: str, viewed_quote: Quote) -> Quote:
        pass

    @abstractmethod
    def get_view(self, quote_id: str, user_id: str) -> View:
        pass

    @abstractmethod
    def mark_as_viewed(self, quote_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    def mark_as_liked(self, quote_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    def like_quote(self, quote_id: str) -> None:
        pass


class APIInterface(ABC):
    @abstractmethod
    def get_random_quote(self) -> Quote:
        pass
