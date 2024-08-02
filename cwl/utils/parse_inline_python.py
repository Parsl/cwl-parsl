import re
from typing import Any, Dict, List, Set

import yaml


def find_references(data: Dict[str, Any], pattern=r"\$\(([^)]+)\)") -> Set:
    """
    Recursively search for all $(...) references in the YAML content.

    Args:
        data (Dict[str, Any]): The YAML content to search for references.
        pattern (str): The regular expression pattern to match references.

    Returns:
        A set of all references found in the YAML content.

    Example:
        ```yaml
        inputs:
            message:
                type: string

        arguments: $(inputs.message)
        ```
        if data is the above YAML content, return "inputs.message"
    """
    references = set()

    if isinstance(data, dict):
        for value in data.values():
            references.update(find_references(value))

    elif isinstance(data, list):
        for item in data:
            references.update(find_references(item))

    elif isinstance(data, str):
        matches = re.findall(pattern, data)
        references.update(matches)
    return references


def get_nested_value(data: Dict[str, Any], key: str) -> Any:
    """
    Retrieve a value from nested dictionaries using a dot-separated key.

    Args:
        data (Dict[str, Any]): The dictionary to search for the value.
        key (str): The dot-separated key to retrieve the value.

    Returns:
        The value corresponding to the key, or None if not found.

    Example:
        ```yaml
        inputs:
            message: "Hello, World!"
        ```
        if data is the above YAML content and key is "inputs.message",
            return "Hello, World!"
    """
    keys = key.split(".")
    value = data
    for k in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(k)
        if value is None:
            return None
    return value


def create_mapping(cwl: Dict[str, Any], inputs: Dict[str, Any]) -> Dict:
    """
    Create a mapping of $(...) references in the CWL content
    to their corresponding values in the inputs.

    Args:
        cwl (Dict[str, Any]): The CWL content containing $(...) references.
        inputs (Dict[str, Any]): The inputs content to map the references to.

    Returns:
        A dictionary mapping references to their corresponding values.

    Example:
        CWL File:
        ```yaml
        inputs:
            message:
                type: string

        arguments: $(inputs.message)
        ```

        Inputs File:
        ```yaml
        inputs:
            message: "Hello, World!"
        ```

        The function will return {"inputs.message": "Hello, World!"}
    """
    reference_pattern = r"\$\(([^)]+)\)"  # $(...) patterns
    all_references = find_references(cwl, reference_pattern)

    mapping = {}
    for ref in all_references:
        value = get_nested_value(inputs, ref)
        if value is not None:
            mapping[ref] = value

    return mapping


def resolve_yaml_references(expression: str, mapping: Dict[str, Any]) -> str:
    """
    Replace $(...) with corresponding values from the mapping dictionary.

    Args:
        expression (str): The expression containing $(...) references.
        mapping (Dict[str, Any]): The dictionary mapping references to values.

    Returns:
        The expression with $(...) references replaced by their values.

    Example:
        If expression is 'f"$(inputs.message)!"' and mapping is
        {"inputs.message": "Hello!"}, the function will return 'f"Hello!"'.
    """
    reference_pattern = r"\$\(([^)]+)\)"

    def replace_reference(match):
        reference = match.group(1)
        if reference in mapping:
            return repr(
                mapping[reference]
            )  # Use repr to ensure proper quoting in eval context
        else:
            raise KeyError(f"Reference '{reference}' not found in mapping.")

    return re.sub(reference_pattern, replace_reference, expression)


def evaluate_expression(expression: str, namespace: Dict[str, Any]) -> Any:
    """
    Evaluate the Python expression inside the f-string.

    Args:
        expression (str): The expression to evaluate.
        namespace (Dict[str, Any]): The namespace to use for evaluation.

    Returns:
        The result of evaluating the expression.

    Example:
        If expression is 'f"{2 + 3}"', the function will return 5.
    """
    try:
        # Evaluate the expression as an f-string by using eval
        return eval(f'f"""{expression}"""', namespace)
    except Exception as e:
        print(f"Error evaluating expression '{expression}': {e}")
        return expression


def evaluate_yaml_expressions(
    data: Dict[str, Any] | List | str,
    namespace: Dict[str, Any],
    mapping: Dict[str, Any],
) -> Dict[str, Any] | List | str:
    """
    Recursively traverse the data structure to evaluate expressions.

    Args:
        data (Dict[str, Any] | List | str): The data structure to traverse.
        namespace (Dict[str, Any]): The namespace for evaluating expressions.
        mapping (Dict[str, Any]): The mapping of references to values.

    Returns:
        The data structure with expressions evaluated.

    Example:
        If data is {"message": 'f"$(inputs.message)!"'} and mapping is
        {"inputs.message": "Hello!"}, the function will return
        {"message": "Hello!"}.
    """
    if isinstance(data, dict):
        # Traverse each key-value pair in the dictionary
        for key, value in data.items():
            data[key] = evaluate_yaml_expressions(value, namespace, mapping)

    elif isinstance(data, list):
        # Traverse each item in the list
        for i, item in enumerate(data):
            data[i] = evaluate_yaml_expressions(item, namespace, mapping)

    elif isinstance(data, str):
        # Check if the string is an f-string expression
        expression_pattern = r'^f"(.+?)"$|^f\'(.+?)\'$'

        if match := re.match(expression_pattern, data):
            # Extract the expression and replace YAML references
            expression = match[1] or match[2]
            resolved_expression = resolve_yaml_references(expression, mapping)
            # Evaluate the resolved Python expression
            return evaluate_expression(resolved_expression, namespace)

    return data


def parse_yaml_file(cwl_file: str, input_file: str) -> Dict[str, Any]:
    """
    Convert a CWL file (yaml) to a dictionary and
    evaluate inline python expressions.

    Args:
        cwl_file (str): The path to the CWL file.
        input_file (str): The path to the input file.

    Returns:
        The parsed and evaluated CWL content.

    Example:
        CWL File:
        ```yaml
        inputs:
            message:
                type: string

        arguments: $(inputs.message)
        ```

        Inputs File:
        ```yaml
        inputs:
            message: "Hello, World!"
        ```

        The function will return the CWL content with expressions evaluated.
        {
            "inputs": {
                "message": {
                    "type": "string"
                }
            },
            "arguments": "Hello, World!"
        }
    """
    with open(cwl_file, "r") as file:
        cwl = yaml.safe_load(file)

    with open(input_file, "r") as file:
        inputs = yaml.safe_load(file)

    namespace = {}
    for func_code in cwl["expressionLib"]:
        exec(func_code, namespace)

    mapping_dict = create_mapping(cwl, inputs)

    evaluate_yaml_expressions(cwl, namespace, mapping_dict)

    return cwl
