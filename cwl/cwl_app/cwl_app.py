"""Module to represent a CWL Command Line Tool and run it using Parsl"""

import os
import pprint
from collections import namedtuple
from concurrent.futures import Executor
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import yaml
from parsl.app.futures import DataFuture
from parsl.data_provider.files import File

from cwl.cwl_app.validate import validate


class InputArgument:
    """Class to represent input arguments for a command line tool"""

    __slots__ = (
        "arg_id",
        "arg_type",
        "array",
        "optional",
        "default",
        "position",
        "prefix",
        "item_separator",
        "separate",
    )

    BOOLEAN = "boolean"
    DOUBLE = "double"
    DIRECTORY = "Directory"
    FILE = "File"
    FLOAT = "float"
    INT = "int"
    LONG = "long"
    STRING = "string"

    def __init__(
        self,
        arg_id: str,
        arg_type: str,
        array: bool = False,
        optional: bool = False,
        default: Optional[Any] = None,
        position: Optional[int] = None,
        prefix: Optional[str] = None,
        item_separator: Optional[str] = None,
        separate: bool = True,
    ) -> None:
        """Class to represent input arguments for a command line tool

        Args:
            id (str): ID of the input argument
            type (str): Type of the input argument - string, int, long, double, float, boolean, File
            array (bool): Is the type an array?
            optional (bool): Is the input argument optional?
            default (Optional[Any]): Default value for the input argument
            position (Optional[int]): Position of the input argument
            prefix (Optional[str]): Add a prefix to the input argument
            item_separator (Optional[str]): Separator for items in the array
            separate (bool): Add a space between the prefix and the input argument
        """

        self.arg_id = arg_id
        self.arg_type = arg_type
        self.array = array
        self.optional = optional
        self.default = default
        self.position = position
        self.prefix = prefix
        self.item_separator = item_separator
        self.separate = separate

    def __repr__(self) -> str:
        return str({slot: getattr(self, slot) for slot in self.__slots__})

    def __str__(self) -> str:
        return str({slot: getattr(self, slot) for slot in self.__slots__})

    def to_string_template(self) -> str:
        """Template string representation of the input argument. Like [-attr=<value>]"""
        if self.arg_type == self.BOOLEAN:
            return f"[{self.prefix}]"

        input_arg_str = ""
        if self.array:
            itm_sep = self.item_separator or " "
            input_arg_str += (
                f"<{self.arg_id}_1{itm_sep}...{itm_sep}{self.arg_id}_n>"
            )

        else:
            input_arg_str += f"<{self.arg_id}>"

        if self.prefix:
            sep = " " if self.separate else ""
            input_arg_str = f"{self.prefix}{sep}{input_arg_str}"

        if self.optional:
            input_arg_str = f"[{input_arg_str}]"

        return input_arg_str

    def to_string(self, value: Any = None) -> str:
        """String representation of the input argument

        Args:
            value (Any, optional): input arg value. Defaults to None.
        """
        if self.arg_type == self.BOOLEAN:
            return self._boolean_to_string(value)

        if value is None:
            value = self.default

        res_string = self._process_value(
            value, str_quote='"' if self.arg_type == self.STRING else ""
        )

        if self.prefix:
            res_string = (
                f"{self.prefix} {res_string}"
                if self.separate
                else f"{self.prefix}{res_string}"
            )

        return res_string

    def _boolean_to_string(self, value: Any) -> str:
        return str(self.prefix) if value and self.prefix else ""

    def _process_value(self, value: Any, str_quote="") -> str:
        if self.array:
            itm_sep = self.item_separator or " "

            return itm_sep.join(
                [self._process_each_value(v, str_quote) for v in value]
            )

        return self._process_each_value(value, str_quote)

    def _process_each_value(self, value: Any, str_quote="") -> str:
        if isinstance(value, (File, DataFuture)):
            return f"{str_quote}{value.filepath}{str_quote}"

        return f"{str_quote}{value}{str_quote}"

    def __lt__(self, other) -> bool:
        if self.position is None:
            return other.position is not None
        return (
            True if other.position is None else self.position < other.position
        )


OutputArgument = namedtuple("Output", ["arg_id", "arg_type", "array"])


class ArgumentMissing(Exception):
    """Exception for missing argument"""

    def __init__(self, message: str) -> None:
        """Exception for missing argument

        Args:
            message (str): Error message
        """
        super().__init__(message)


class CWLApp:
    """Class to represent a CWL Command Line Tool and run it using Parsl"""

    @classmethod
    def _bash_app(
        cls,
        command: str,
        stdout: str,
        stderr: str,
        inputs,
        outputs,
    ):
        return command

    def __init__(self, cwl: str | Dict[str, Any], executor: Executor) -> None:
        """Command Line Tool

        Args:
            cwl (str | Dict[str, Any]):
                Path to the CWL file or
                CWL file content represented as a dictionary

            executor (Executor): Parsl executor
        """

        if isinstance(cwl, dict):
            cwl_content = cwl

        else:
            with open(cwl, "r", encoding="utf-8") as f:
                cwl_content = yaml.safe_load(f)

        validate(cwl_content)

        self._file_name = cwl
        self._cwl_content = cwl_content
        self._version = self._cwl_content["cwlVersion"]
        self._base_command = None
        self._arguments: List[str] = []
        self._inputs: List[InputArgument] = []
        self._outputs: List[OutputArgument] = []
        self._executor = executor
        self._stdout = None
        self._stderr = None
        self.run_ids = []

        self._set_cwl_args()

    def _set_cwl_args(self) -> None:
        if isinstance(self._cwl_content["baseCommand"], list):
            self._base_command = " ".join(self._cwl_content["baseCommand"])
        else:
            self._base_command = self._cwl_content["baseCommand"]

        if "arguments" in self._cwl_content:
            self._arguments = self._cwl_content["arguments"]

        self._set_inputs(self._cwl_content["inputs"])

        if "outputs" in self._cwl_content:
            self._set_outputs(self._cwl_content["outputs"])

    def __str__(self) -> str:
        return pprint.pformat(self._cwl_content)

    def __call__(self, **kwargs: Any):
        """Run the CWL CommandLineTool using Parsl

        Expects: input and output arguments mentioned in the CWL file

        Make sure to use the same names for function parameters as
        the input and output arguments in the CWL file.
        """
        run_id = uuid4()
        self.run_ids.append(run_id)

        args = self._get_parsl_bash_app_args(**kwargs)
        return self._executor.submit(self._bash_app, **args)

    def _set_inputs(
        self, cwl_inputs: Union[List[Dict[str, Any]], Dict[str, any]]
    ) -> None:
        """Set input options from CWL

        Args:
            cwl_inputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL inputs
        """
        inputs = []

        def process_input(arg_id, input_arg):
            if input_arg["type"] == "array":
                arg_type = input_arg["items"]
                array = True

            else:
                arg_type = input_arg["type"].rstrip("[]").rstrip("?")
                array = "[]" in input_arg["type"]

            optional = "?" in input_arg["type"]
            default = input_arg.get("default", None)
            position = input_arg.get("inputBinding", {}).get("position", None)
            prefix = input_arg.get("inputBinding", {}).get("prefix", None)
            item_separator = input_arg.get("inputBinding", {}).get(
                "itemSeparator", None
            )
            separate = input_arg.get("inputBinding", {}).get("separate", True)

            return InputArgument(
                arg_id,
                arg_type,
                array,
                optional,
                default,
                position,
                prefix,
                item_separator,
                separate,
            )

        if isinstance(cwl_inputs, list):
            inputs.extend(
                process_input(input_arg["id"], input_arg)
                for input_arg in cwl_inputs
            )

        elif isinstance(cwl_inputs, dict):
            inputs.extend(
                process_input(id, input_arg_opts)
                for id, input_arg_opts in cwl_inputs.items()
            )

        inputs.sort()
        self._inputs = inputs

    def _set_outputs(
        self, cwl_outputs: Union[List[Dict[str, Any]], Dict[str, any]]
    ) -> None:
        """Set output options from CWL

        Args:
            cwl_outputs (Union[List[Dict[str, Any]], Dict[str, any]]): CWL outputs
        """
        outputs = []

        def process_output(arg_id, output_arg):
            arg_type = output_arg["type"]
            if arg_type == "array":
                arg_type = output_arg["items"]
                array = True

            else:
                arg_type = output_arg["type"].rstrip("[]")
                array = "[]" in output_arg["type"]

            return OutputArgument(arg_id, arg_type, array)

        if isinstance(cwl_outputs, list):
            outputs.extend(
                process_output(output_arg["id"], output_arg)
                for output_arg in cwl_outputs
            )

        elif isinstance(cwl_outputs, dict):
            outputs.extend(
                process_output(id, output_arg_opts)
                for id, output_arg_opts in cwl_outputs.items()
            )

        self._outputs = outputs

    @property
    def command_template(self) -> str:
        """Synopsis/Template for the command.

        Returns:
            str: template string to show example usage
        """
        return (
            f"COMMAND TEMPLATE:\n{self._base_command} "
            f"{' '.join(self._arguments) if self._arguments else ''} "
            f"{' '.join([input_arg.to_string_template() for input_arg in self._inputs])}"
        )

    @property
    def cwl_version(self) -> str:
        """CWL version"""
        return self._version

    @property
    def cwl_file_name(self) -> str:
        """CWL file name"""
        return os.path.basename(self._file_name)

    @property
    def stdout_filename(self) -> str:
        """Returns the stdout file name from the most recent run.
        stdout file name is created only after the execution of the cwl"""
        return None if self._stdout is None else self._stdout

    @property
    def stderr_filename(self) -> str:
        """Returns the stderr file name from the most recent run.
        stderr file name is created only after the execution of the cwl"""
        return self._stderr

    def get_command(self, **kwargs) -> str:
        """Shell command to be run.

        kwargs: input parameters

        Returns:
            str: string of the shell command that is to be run
        """
        input_args = []
        for input_arg in self._inputs:
            if input_arg.arg_id in kwargs:
                input_args.append(input_arg.to_string(kwargs[input_arg.arg_id]))

            elif input_arg.default:
                input_args.append(input_arg.to_string())

            elif input_arg.optional:
                continue

            else:
                raise ArgumentMissing(
                    f"missing required value for argument: {input_arg.arg_id}"
                )

        # filter out None values
        return " ".join(
            filter(
                None,
                [
                    self._base_command,
                    f"{' '.join(filter(None, self._arguments))}",
                    f"{' '.join(filter(None, input_args))}",
                ],
            )
        )

    def _get_parsl_bash_app_args(self, **kwargs) -> Dict[str, Any]:
        """Args needed to run the command using Parsl

        kwargs: values for inputs and outputs mentioned in the CWL file

        Returns: Dict[str, Any]: Args needed to run the command using Parsl
                args = {
                    "command": str,
                    "stdout": File,
                    "stderr": File,
                    "inputs": [File],
                    "outputs": [File],
                }
        """

        # Check if all the output arguments are provided
        for output_arg in self._outputs:
            # handle stdout and stderr
            if output_arg.arg_type == "stdout":
                if output_arg.arg_id not in kwargs:
                    self._stdout = (
                        f"stdout_{self._file_name}_{self.run_ids[-1]}.txt"
                    )
                else:
                    self._stdout = kwargs[output_arg.arg_id]

            elif output_arg.arg_type == "stderr":
                if output_arg.arg_id not in kwargs:
                    self._stderr = (
                        f"stderr_{self._file_name}_{self.run_ids[-1]}.txt"
                    )
                else:
                    self._stderr = kwargs[output_arg.arg_id]

            # elif (
            #     output_arg.arg_type == "File"
            #     and output_arg.arg_id not in kwargs
            # ):
            #     raise ArgumentMissing(
            #         f"missing required value for argument: {output_arg.arg_id}"
            #     )

        def handle_input_output_files(file):
            if file.arg_type != "File" or file.arg_id not in kwargs:
                return []

            if file.array:
                files = []
                for f in kwargs[file.arg_id]:
                    if isinstance(f, str):
                        files.append(File(f))
                    else:
                        files.append(f)

                return files

            # convert str to Parsl File
            if isinstance(kwargs[file.arg_id], str):
                return [File(kwargs[file.arg_id])]

            return [kwargs[file.arg_id]]

        # list input files
        input_files = []
        for file in self._inputs:
            input_files.extend(handle_input_output_files(file))

        # list output files
        output_files = []
        for file in self._outputs:
            output_files.extend(handle_input_output_files(file))

        # get command string
        command = self.get_command(**kwargs)

        cmd_args = {
            "command": command,
            "stdout": self._stdout,
            "stderr": self._stderr,
            "inputs": input_files,
            "outputs": output_files,
        }

        return cmd_args
