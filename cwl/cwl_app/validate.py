from typing import Dict

from schema import And
from schema import Optional as Opt
from schema import Or, Regex, Schema, SchemaError


class InvalidCWL(Exception):
    """Exception for invalid CWL file"""

    def __init__(self, message: str) -> None:
        """Exception for invalid CWL file

        Args:
            message (str): Error message
        """
        super().__init__(message)


def validate(cwl_content: Dict[str, any]) -> Dict[str, any]:
    """Check if CWL is valid.

    Args:
        cwl_content (Dict[str, Any]): CWL file for the command

    Raises:
        schema.SchemaError if CWL is invalid

    Returns:
        Dict[str, Any]: Original CWL contents if valid
    """

    input_binding_schema = And(
        {
            Opt("position"): int,
            Opt("prefix"): str,
            Opt("separate"): bool,
            Opt("itemSeparator"): str,
        },
        len,
        error="Empty inputBinding.",
    )

    input_simple_types = [
        "array",
        "boolean",
        "int",
        "long",
        "float",
        "double",
        "string",
        "File",
    ]
    input_array_types = [f"{t}[]" for t in input_simple_types]
    input_optional_types = [f"{t}?" for t in input_simple_types]

    input_types_schema = Or(
        *input_simple_types,
        *input_array_types,
        *input_optional_types,
        error=(
            "Invalid type for input."
            "Should be one of array, boolean, int, long, float, double, string, File"
            "Can be optional or array of these types"
        ),
    )

    output_types_schema = Or(
        "stdout",
        "stderr",
        "File",
        "File[]",
        "array",
        error=(
            "Invalid type for output."
            "Should be stdout, stderr, File, File[] or array with items of type File"
        ),
    )

    cmd_line_tool_schema = Schema(
        {
            "cwlVersion": Regex(
                r"^v[0-9]+(\.[0-9]+){0,2}$", error="Invalid CWL Version"
            ),
            "baseCommand": Or(
                [str], str, error="Invalid type for Base Command"
            ),
            "class": And(
                str,
                lambda cls: cls == "CommandLineTool",
                error="Invalid type for class. Should be 'CommandLineTool'.",
            ),
            Opt("arguments"): Or(
                [str], str, error="Invalid type for arguments"
            ),
            "inputs": Or(
                {
                    Regex(
                        r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                    ): {
                        "type": input_types_schema,
                        Opt("items"): Or(*input_simple_types),
                        Opt("default"): Or(
                            int,
                            float,
                            str,
                            bool,
                            list,
                            error="Invalid default value",
                        ),
                        Opt("inputBinding"): input_binding_schema,
                    }
                },
                [
                    {
                        "id": Regex(
                            r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                        ),
                        "type": input_types_schema,
                        Opt("items"): Or(*input_simple_types),
                        Opt("default"): Or(
                            int,
                            float,
                            str,
                            bool,
                            list,
                            error="Invalid default value",
                        ),
                        Opt("inputBinding"): input_binding_schema,
                    }
                ],
                error=("Invalid/Empty 'inputs'."),
            ),
            "outputs": Or(
                {
                    Regex(
                        r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                    ): {
                        "type": output_types_schema,
                        Opt("items"): "File",
                        Opt("outputBinding"): any,
                    }
                },
                [
                    {
                        "id": Regex(
                            r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                        ),
                        "type": output_types_schema,
                        Opt("items"): "File",
                        Opt("outputBinding"): any,
                    }
                ],
                error=("Invalid/Empty 'outputs'."),
            ),
            Opt(any): any,
        },
    )

    try:
        return cmd_line_tool_schema.validate(cwl_content)

    except SchemaError as e:
        raise InvalidCWL(
            "Invalid Cwl File for Command Line Tools\n"
            + "\n".join({exp for exp in e.errors if exp})
        ) from None
