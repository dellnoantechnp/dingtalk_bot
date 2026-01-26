from abc import ABC, abstractmethod
from typing import Optional


class AbstractIMClient(ABC):
    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def update(self, user_id: Optional[str]):
        pass