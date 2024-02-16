import os

from cwl import CWLApp

# Create CommandLineTool objects CWL files

cat = CWLApp(os.path.join("tools", "cwl_files", "cat.cwl"))

find = CWLApp(os.path.join("tools", "cwl_files", "find.cwl"))

touch = CWLApp(os.path.join("tools", "cwl_files", "touch.cwl"))

wc = CWLApp(os.path.join("tools", "cwl_files", "wc.cwl"))

# etc...
