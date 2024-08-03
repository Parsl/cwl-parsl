from typing import Dict, Sequence, Tuple
from cwl.utils.parse_inline_python import parse_yaml_file

import yaml


def parse_args(
    executor_config_file: str,
    cwl_file: str,
    inputs_file: str,
) -> Tuple[Dict, Dict, Dict]:
    try:
        with open(executor_config_file, "r") as f:
            executor_options = yaml.safe_load(f)

        cwl_content = parse_yaml_file(cwl_file, inputs_file)

        with open(inputs_file, "r") as f:
            inputs_content = yaml.safe_load(f)

        return (executor_options, cwl_content, inputs_content)

    except ValueError as e:
        raise ValueError("Usage: cwl-run <cwl_file> <executor_name>") from e
