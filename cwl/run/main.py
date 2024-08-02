import sys
from concurrent.futures import Future
from typing import Sequence, Tuple

from pydantic import ValidationError

from cwl.cwl_app import CWLApp
from cwl.run.config import Config
from cwl.run.parse import parse_args_to_config


def run(config: Config, fn, *args, **kwargs) -> Tuple[CWLApp, Future]:
    cwl = config.get_cwl()
    executor = config.get_executor()

    app = CWLApp(cwl, executor)
    fut = app(fn, *args, **kwargs)

    return (app, fut)


def main(
    fn,
    argv: Sequence[str] | None = None,
    *args,
    **kwargs,
) -> None:
    argv = argv or sys.argv[1:]

    try:
        config = parse_args_to_config(argv)

    except ValidationError as e:
        print(e)
        sys.exit(1)

    try:
        return run(config, fn, *args, **kwargs)

    except BaseException as e:
        print(e)
        sys.exit(1)
