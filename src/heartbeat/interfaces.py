from abc import ABC, abstractmethod


class DBInterface(ABC):
    @abstractmethod
    def ping(self) -> None:
        pass
