import sys

from cwl import ParslCWLTool

if __name__ == "__main__":
    USAGE = (
        "Usage: python3 parsl_cwl_tool.py <cwl_file> --<input1>=<value1> --<input2>=<value2> ...--stdout=<value3> ...\n"
        "or\n"
        "Usage: python3 parsl_cwl_tool.py <cwl_file> <yaml_file>"
    )
    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit(1)

    args = sys.argv
    parsl_cwl_tool = ParslCWLTool(*args)
    parsl_cwl_tool.result()
