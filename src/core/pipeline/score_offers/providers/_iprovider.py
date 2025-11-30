from abc import ABC, abstractmethod


class IProvider(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, temp: float = 0, top_p: float = 1) -> str:
        pass
