from abc import ABC, abstractmethod

from dingtalk.Schema.APISchema import APISchema


class AbstractIMClient(ABC):
    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def update(self):
        pass