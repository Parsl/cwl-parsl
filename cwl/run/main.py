import sys
from concurrent.futures import Executor, Future
from typing import Any, Dict, Sequence, Tuple

from pydantic import ValidationError

from cwl.cwl_app import CWLApp
from cwl.executors.executor import create_executor as _create_new_executor
from cwl.run.parse import parse_args


def run(
    cwl: str, executor: Executor, fn, *args, **kwargs
) -> Tuple[CWLApp, Future]:
    """Create and run CWL App with the given inputs

    Args:
        cwl (str): Path to the cwl file
        executor (Executor): Executor object
        *args: Args for the function
        **kwargs: Kwargs for the function
    """
    app = CWLApp(cwl, executor)
    fut = app(fn, *args, **kwargs)

    return (app, fut)


def create_cwl_app(cwl: str, executor: Executor) -> CWLApp:
    """Create CWL App for the given cwl file

    Args:
        cwl (str): Path to the cwl file
        executor (Executor): Executor object

    Returns:
        CWLApp: CWLApp object
    """

    return CWLApp(cwl, executor)


def create_executor(executor_options: Dict[str, Any]) -> Executor:
    """Create an executor object

    Args:
        executor_options: Configuration options for the executor
        {
            "executor": "parsl",
            "config": {
                "type": "htex" | "thread",
                "options": Dict[str, Any]  # Options for the parsl config
            }
        }

    Returns:
        Executor object
    """
    return _create_new_executor(executor_options)


def main(argv: Sequence[str] | None = None) -> None:
    config, cwl_file, inputs_file = argv or sys.argv[1:]

    try:
        return parse_args(argv)

    except ValidationError as e:
        print(e)
        sys.exit(1)
