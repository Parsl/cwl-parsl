from abc import ABC, abstractmethod
from concurrent.futures import Executor


class BaseConfig(ABC):
    @abstractmethod
    def get_executor(self) -> Executor:
        pass

    @abstractmethod
    def get_cwl(self) -> str:
        pass


class Config(BaseConfig):

    def __init__(self, cwl: str, executor: Executor) -> None:
        self.cwl = cwl
        self.executor = executor

    def get_executor(self) -> Executor:
        return self.executor

    def get_cwl(self) -> str:
        return self.cwl
