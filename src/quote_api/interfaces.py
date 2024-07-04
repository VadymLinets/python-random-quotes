from abc import ABC, abstractmethod

from src.quote.models import Quote


class DBInterface(ABC):
    @abstractmethod
    def save_quote(self, quote: Quote) -> None:
        pass
