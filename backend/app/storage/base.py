from abc import ABC, abstractmethod
from typing import Any


class StorageAdapter(ABC):
    @abstractmethod
    def read(self, key: str, default: Any = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def write(self, key: str, payload: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError
