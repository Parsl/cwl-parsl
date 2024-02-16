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