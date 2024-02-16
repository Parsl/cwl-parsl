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
    type: int
    default: 3
    inputBinding:
      prefix: -maxdepth
      position: 3

outputs:
  example_out:
    type: stdout