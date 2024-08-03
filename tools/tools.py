"""List of CWL CommandLineTool CWLApps"""

import os

from cwl import CWLApp
from cwl.executors.executor import create_executor

# Create CommandLineTool objects CWL files

executor = create_executor(
    {
        "executor": "parsl",
        "config": {
            "type": "thread",
            "options": {},
        },
    }
)

cat = CWLApp(os.path.join("tools", "cwl_files", "cat.cwl"), executor)

find = CWLApp(os.path.join("tools", "cwl_files", "find.cwl"), executor)

touch = CWLApp(os.path.join("tools", "cwl_files", "touch.cwl"), executor)

wc = CWLApp(os.path.join("tools", "cwl_files", "wc.cwl"), executor)
