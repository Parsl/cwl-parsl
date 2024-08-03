from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import Any, Dict


class BaseConfig(ABC):
    @abstractmethod
    def get_executor(self) -> Executor:
        pass

    @abstractmethod
    def get_cwl(self) -> Any:
        pass

    @abstractmethod
    def get_inputs(self) -> Any:
        pass


class Config(BaseConfig):

    def __init__(
        self, executor: Executor, cwl: Dict[str, Any], inputs: Dict[str, Any]
    ) -> None:
        self._executor = executor
        self._cwl = cwl
        self._inputs = inputs

    def get_executor(self) -> Executor:
        return self._executor

    def get_cwl(self) -> Dict[str, Any]:
        return self._cwl

    def get_inputs(self) -> Dict[str, Any]:
        return self._inputs
