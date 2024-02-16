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

  redirect_to_file:
    type: string
    inputBinding:
      position: 4
      prefix: ">>"
      separate: true

outputs:
  output_file:
    type: File