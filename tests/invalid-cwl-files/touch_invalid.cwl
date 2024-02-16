cwlVersion: v1.0
class: CommandLineTool
baseCommand: touch

inputs:
  file-names: # invalid name for python variable
    type: string[]
    inputBinding:
      position: 1
      separate: true

outputs:
  output-files: # invalid name for python variable
    type: array
    items: File
    outputBinding:
      glob: $(inputs.filenames)