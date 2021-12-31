from abc import ABC, abstractmethod


class UseCase(ABC):

    @abstractmethod
    def exec(self):
        ...
