from concurrent.futures import Executor
from typing import Any, Dict

from cwl.executors.parsl import CWLExecutor, ParslConfig


def create_executor(config_options: Dict[str, Any]) -> Executor:
    """Create an executor object

    Args:
        config_options: Configuration options for the executor
        {
            "executor": "parsl",
            "config": {
                "type": "htex" | "thread",
                "options": Dict[str, Any]  # Options for the parsl config
            }
        }
    """
    executor = config_options["executor"]
    config = config_options["config"]

    if executor == "parsl":
        parsl_config = ParslConfig(config)
        return CWLExecutor(parsl_config.get_config())

    else:
        raise ValueError(f"Unknown executor type: {executor}")
