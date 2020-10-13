import builtins
from typing import Optional
from buffer import Buffer
from deepline_error import DeeplineError


# Inserts text at next line of whatever buffer index is pointing at
def insert(buffer: Buffer, text: str):
    lines = text.split("\n")
    if buffer.current_line_index is None:
        buffer.current_line_index = len(lines) - 1
        buffer.lines = lines
    else:
        insert_pos = buffer.current_line_index + 1
        buffer.lines[insert_pos:insert_pos] = lines
        buffer.current_line_index += len(lines)


# Reads a given textfile and inserts text at the end calling insert()
def read(buffer: Buffer, filename: Optional[str]):
    if filename is None:
        if buffer.current_file is None:
            raise DeeplineError("No filename provided")
        else:
            filename = buffer.current_file
    else:
        buffer.current_file = filename

    with open(filename, "r") as f:
        file_contents = f.read()
        insert(buffer, file_contents)


# Writes whats in the buffer to a given textfile
def write(buffer: Buffer, filename: Optional[str]):
    if filename is None:
        if buffer.current_file is None:
            raise DeeplineError("No filename provided")
        else:
            filename = buffer.current_file
    else:
        buffer.current_file = filename

    with open(filename, "w") as f:
        f.write("\n".join(buffer.lines))


def current_line(buffer: Buffer, integer: int):
    if integer >= len(buffer.lines):
        raise DeeplineError("Line number out range")
    else:
        buffer.current_line_index = integer


# Prints whats in the buffer
def print(buffer: Buffer):
    for line in buffer.lines:
        builtins.print(line)
