import Buffer

def insert(buffer, text):
    lines = text.split("\n")
    if buffer.current_line_index is None:
        buffer.current_line_index = len(lines) - 1
        buffer.lines = lines
    else:
        buffer.lines.insert(buffer.current_lines_index + 1, lines)
        buffer.current_line_index += len(lines)

def read(buffer, filename):
    with open(filename, "r") as f:
	    file_contents = f.read()
        buffer.lines = file_contents

def write(buffer):
    pass

def print(buffer):
    for line in buffer.lines:
        print(line)