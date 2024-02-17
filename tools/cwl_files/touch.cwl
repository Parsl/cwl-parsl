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
  stdout:
    type: stdout
  stderr:
    type: stderr