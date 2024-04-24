"""Module to represent a command line tool for CWLApp."""

import ast

import parsl
import yaml
from parsl.configs.local_threads import config

from cwl import ArgumentMissing, CWLApp

parsl.load(config)


class InvalidArgumentError(Exception):
    """Exception to raise when invalid arguments are passed to the script."""

    def __init__(self, message):
        print("INVALID ARGUMENTS\n")
        super().__init__(message)


class ParslCWLTool:
    """Class to represent a command line tool for CWLApp."""

    def __init__(self, *cwl_args):
        if not cwl_args[1].endswith(".cwl"):
            raise ValueError(f"Invalid CWL file: {cwl_args[1]}")

        self.cwl_app = CWLApp(cwl_args[1])
        self.app_future = self.run(cwl_args)

    def run(self, cwl_args: list[str]):
        """Run the CWLApp with the given inputs and outputs."""
        cwl_inputs_outputs = {}

        try:
            if len(cwl_args) == 3 and cwl_args[2].endswith(".yml"):
                with open(cwl_args[2], "r", encoding="utf-8") as f:
                    cwl_inputs_outputs = yaml.safe_load(f)

            else:
                for arg in cwl_args[2:]:
                    key, value = arg.split("=")
                    cwl_inputs_outputs[key.lstrip("--")] = (
                        ast.literal_eval(value)
                        if value.startswith("[") and value.endswith("]")
                        else value
                    )

        except ArgumentMissing as e:
            raise InvalidArgumentError(str(e)) from e

        except Exception as e:
            raise InvalidArgumentError(str(e)) from e

        return self.cwl_app(**cwl_inputs_outputs)

    def result(self):
        """Print the result of running the CWL with given inputs and outputs
        using CWLApp."""
        try:
            self.app_future.result()

            if self.app_future.stdout:
                print("STDOUT:")
                with open(self.app_future.stdout, "r", encoding="utf-8") as f:
                    print(f.read())

        except Exception:
            if self.app_future.stderr:
                print("STDERR:")
                with open(self.app_future.stderr, "r", encoding="utf-8") as f:
                    print(f.read())
