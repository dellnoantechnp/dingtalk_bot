from abc import ABC, abstractmethod


class IM_Client(ABC):
    @abstractmethod
    def send(self):
        pass

    def update(self):
        pass