from concurrent.futures import Executor
from typing import Any, Dict

from cwl.executors.parsl import CWLExecutor, ParslConfig


def create_executor(config_options: Dict[str, Any] | None = None) -> Executor:
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
    if config_options is None:
        return CWLExecutor(
            ParslConfig({"type": "thread", "options": {}}).get_config()
        )

    executor = config_options["executor"]
    config = config_options["config"]

    if executor == "parsl":
        parsl_config = ParslConfig(config)
        return CWLExecutor(parsl_config.get_config())

    else:
        raise ValueError(f"Unknown executor type: {executor}")
