cwlVersion: v1.0
class: CommandLineTool
baseCommand: wc

inputs:
  text_file:
    type: File
    inputBinding:
      position: 1

outputs:
  - id: stdout
    type: stdout