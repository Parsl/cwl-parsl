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