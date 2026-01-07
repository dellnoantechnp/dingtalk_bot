from abc import ABC, abstractmethod


class AbstractIMClient(ABC):
    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def update(self):
        pass