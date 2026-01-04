from abc import ABC, abstractmethod


class IM_Client(ABC):
    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def update(self):
        pass