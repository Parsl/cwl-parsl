cwlVersion: v1.0
class: CommandLineTool
baseCommand: wc

inputs:
  text_file:
    type: File
    inputBinding:
      position: 1

  text_file_2:
    type: File
    inputBinding:
      position: 1

outputs:
    stdout:
      type: stdout- # Expected: stdout