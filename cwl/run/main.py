import sys
from concurrent.futures import Executor, Future
from typing import Any, Dict, Sequence, Tuple

from pydantic import ValidationError

from cwl.cwl_app import CWLApp
from cwl.executors.executor import create_executor as _create_new_executor
from cwl.run.config import Config
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


def create_config(
    executor_options: Dict[str, Any],
    cwl_content: Dict[str, Any],
    inputs_content: Dict[str, Any],
) -> Config:
    """Create a config object

    Args:
        executor_options (Dict[str, Any]): Config options for the executor
        cwl_content (Dict[str, Any]): CWL content parsed from the file
        inputs_content (Dict[str, Any]): Inputs content parsed from the file
    """

    executor = create_executor(executor_options)

    return Config(executor, cwl_content, inputs_content)


def main(argv: Sequence[str] | None = None) -> None:
    # TODO: cache bash app and run everything from here
    executor_config_file, cwl_file, inputs_file = argv or sys.argv[1:]

    try:
        executor_options, cwl_content, inputs_content = parse_args(
            executor_config_file, cwl_file, inputs_file
        )

        config = create_config(executor_options, cwl_content, inputs_content)
        app = create_cwl_app(config.get_cwl(), config.get_executor())
        return (app, config.get_inputs())

    except ValidationError as e:
        print(e)
        sys.exit(1)
