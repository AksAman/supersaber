from abc import ABC, abstractmethod


class Publisher(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def publish(self, topic: str, payload: str):
        pass

    @abstractmethod
    def disconnect(self):
        pass
