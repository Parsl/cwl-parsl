# Command Line Tool app tutorial

Command Line Tool is a python app that allows you to integrate CWL 'CommandLineTool' files with parsl.

Parsl is a python parallel scripting library. 

Learn about Parsl [here](https://parsl.readthedocs.io/en/stable/index.html)

## Getting started

### Example: echo.cwl

```yml
cwlVersion: v1.0
class: CommandLineTool

baseCommand: echo

inputs:
  message:
    type: string
    inputBinding:
      position: 1

outputs:
  stdout:
    type: stdout
```

### Creating a CommandLineTool app
```python
from cwl import CommandLineTool

# app takes one argument - path to cwl file
echo = CWLApp("echo.cwl")
print(echo.command_template)
```

### Output
```bash
COMMAND TEMPLATE:
echo <message>
```

---
### Running CommandLineTool app with Parsl

CWLApp uses Parsl's bash_app internally for running the CommandLineTools and returns a DataFuture.

DataFutures represent the files produces by execution of an asynchronous app. Parsl’s dataflow model, in which data flows from one app to another via files, requires such a construct to enable apps to validate creation of required files and to subsequently resolve dependencies when input files are created. When invoking an app, Parsl requires that a list of output files be specified (using the ```outputs``` keyword argument). A DataFuture for each file is returned by the app when it is executed. Throughout execution of the app, Parsl will monitor these files to 1) ensure they are created, and 2) pass them to any dependent apps.

Learn more about bash_app, DataFuture [here](https://parsl.readthedocs.io/en/stable/1-parsl-introduction.html#Bash-Apps)

### Example 1: find.cwl - cwl for the 'find' command
```yml
cwlVersion: v1.2
class: CommandLineTool
baseCommand: find

inputs:
  dir:
    type: string
    inputBinding:
      position: 1

  name:
    type: string?
    inputBinding:
      prefix: -name
      separate: true
      position: 2

  maxdepth:
    type: int?
    inputBinding:
      prefix: -maxdepth
      position: 3

outputs:
  example_out:
    type: stdout
```

```python
find = CWLApp("find.cwl")
print(find.command_template)
# find <dir> [-name <name>] [-maxdepth <maxdepth>]

find(dir=".", maxdepth=3, name="*.docx", example_out="find_stdout.txt").result()

with open("find_stdout.txt", "r") as f:
    print(f.read())
```

### What's Executed:
```
$ find '.' -name '*.docx' -maxdepth 3
```

Running the CommandLineTool expects the same arguments as mentioned in the inputs and outputs section of the cwl
</br>
Args can be optional and left out and can have default values which will be used if left out

```python
find(dir=".", example_out="find_stdout.txt").result()
```

### What's Executed:
```
$ find '.'
```
---

### Example 2: wc.cwl - word count

Create and use parsl File objects for all inputs/outputs that have type 'File'

```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: wc

inputs:
  len_line_most_bytes:
    type: boolean?
    inputBinding:
      position: 1
      prefix: -L

  num_bytes:
    type: boolean?
    inputBinding:
      position: 2
      prefix: -c
  
  num_lines:
    type: boolean?
    inputBinding:
      position: 3
      prefix: -l
  
  num_chars:
    type: boolean?
    inputBinding:
      position: 4
      prefix: -m
  
  num_words:  
    type: boolean?
    inputBinding:
      position: 5
      prefix: -w

  input_files:
    type: File[]
    inputBinding:
      position: 6

outputs:
  stdout:
    type: stdout
  stderr:
    type: stderr
```

```python
from parsl.data_provider.files import File

wc = CWLApp("wc.cwl")

wc(input_files=[File("test_file.txt")], stdout="wc_stdout.txt").result()

with open("wc_stdout.txt", "r") as f:
    print(f.read())
```

### What's Executed:
```
$ wc test_file.txt
```
---

### Example 3: touch.cwl - create files
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: touch

inputs:
  filenames:
    type: string[]
    inputBinding:
      position: 1
      separate: true

outputs:
  output_files:
    type: array
    items: File
    outputBinding:
      glob: $(inputs.filenames)
```

```python
touch = CWLApp("touch.cwl")

touch(
  filenames=["file_name_1.txt", "file_name_2.txt"],
  output_files=[
    File("file_name_1.txt"),
    File("file_name_2.txt")
  ]
).result()
```

### What's Executed:
```
$ touch 'file_name_1.txt' 'file_name_2.txt'
```
---

### Example 4: cat.cwl - Cat contents of file(s) to another file
```yml
cwlVersion: v1.0
class: CommandLineTool
baseCommand: cat

inputs:
  from_files:
    type: File[]
    inputBinding:
      position: 1
    
  to_file:
    type: string
    inputBinding:
      position: 2
      prefix: ">>"
      separate: true

outputs:
  output_file:
    type: File
```

```python
cat = CWLApp("cat.cwl")
cat(from_files=[File("test_file.txt")], to_file="cat_stdout.txt", output_file=File("cat_stdout.txt")).result()
```

### What's Executed:
```
$ cat test_file.txt >> 'cat_stdout.txt'
```

---

### Example 5: Combination of CWLapps
create the CWLapp once and reuse or forward outputs of one app to another same as parsl

```python
import os

from parsl.data_provider.files import File

from tools import cat

q1 = cat(
    from_files=[
        File(os.path.join("reports", "january_report.csv")),
        File(os.path.join("reports", "february_report.csv")),
        File(os.path.join("reports", "march_report.csv")),
    ],
    to_file="q1_report.csv",
    output_file=File("q1_report.csv"),
)

q2 = cat(
    from_files=[
        File(os.path.join("reports", "april_report.csv")),
        File(os.path.join("reports", "may_report.csv")),
        File(os.path.join("reports", "june_report.csv")),
    ],
    to_file="q2_report.csv",
    output_file=File("q2_report.csv"),
)

half_year_report = cat(
    from_files=[q1.outputs[0], q2.outputs[0]],
    to_file="half_year_report.csv",
    output_file=File("half_year_report.csv"),
)

half_year_report.result()

with open("half_year_report.csv", "r") as f:
    print(f.read())

```

---

### Example 6: cat and wc

Combine files using 'cat' and use 'wc' to count lines, words, bytes etc

```python
from parsl.data_provider.files import File

from tools import cat, wc

cat_future = cat(
    from_files=[
        File("file1.txt"),
        File("file2.txt"),
        File("file3.txt"),
    ],
    to_file="combined.txt",
    output_file=File("combined.txt"),
)

wc(
    num_lines=True,
    num_words=True,
    input_files=[cat_future.outputs[0]],
    stdout="wc_stdout.txt",
    stderr="wc_stderr.txt",
).result()

with open("wc_stdout.txt", "r") as f:
    print(f.read())
```