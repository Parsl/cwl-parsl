from concurrent.futures import Executor
from typing import Any, Dict, Sequence

from cwl.executors import CWLExecutor
from cwl.run.config import Config


def parse_args(argv: Sequence[str]) -> Config:
    try:
        config, cwl_file, inputs_file = argv

    except ValueError as e:
        raise ValueError("Usage: cwl-run <cwl_file> <executor_name>") from e
