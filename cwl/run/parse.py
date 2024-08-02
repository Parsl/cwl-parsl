from concurrent.futures import Executor
from typing import Sequence

from cwl.executors import CWLExecutor
from cwl.run.config import Config


def _get_executor(executor_name: str) -> Executor:
    if executor_name == "parsl":
        return CWLExecutor()
    else:
        raise ValueError(f"Unknown executor: {executor_name}")


def parse_args_to_config(argv: Sequence[str]) -> Config:
    try:
        cwl_file, executor_name = argv
        return Config(cwl=cwl_file, executor=_get_executor(executor_name))

    except ValueError as e:
        raise ValueError("Usage: cwl-run <cwl_file> <executor_name>") from e
