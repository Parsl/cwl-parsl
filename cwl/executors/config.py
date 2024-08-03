from abc import ABC, abstractmethod
from typing import Any


class ExecutorConfig(ABC):
    @abstractmethod
    def get_config(self) -> Any:
        pass
