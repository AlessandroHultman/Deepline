from buffer import Buffer
import re
from typing import Tuple, Optional
from copy import copy


def range(buffer: Buffer, text: str) -> Optional[Tuple[str, Buffer]]:
    # Check wether buffer is empty.
    if buffer.current_line_index is None:
        return None
    buffer = copy(buffer)

    # Parse the first address.
    address_match = parse_address(buffer, text)
    if address_match is not None:
        text = address_match[0]
        first_address: Optional[int] = address_match[1]
        if address_match[1] >= len(buffer.lines):
            raise Exception(
                f"First address: {first_address}, is out of range of the buffer"
            )
    else:
        first_address = None

    # Check the midle of the range.
    if text.startswith(","):
        text = text[1:]
        if first_address is None:
            first_address = 0
    elif text.startswith(";"):
        text = text[1:]
        if first_address is None:
            first_address = buffer.current_line_index
        buffer.current_line_index = first_address
    else:
        if first_address is not None:
            last_address = first_address
        else:
            return None
    assert (first_address is not None)

    # Parse the last address.
    address_match = parse_address(buffer, text)
    if address_match is not None:
        text = address_match[0]
        last_address = address_match[1]
        if last_address >= len(buffer.lines):
            raise Exception(
                f"Last address: {last_address}, is out of range of the buffer")
    else:
        last_address = len(buffer.lines) - 1

    if last_address < first_address:
        raise Exception(
            "Last address cannot be smaller than first address in range")

    buffer.lines = buffer.lines[first_address:last_address + 1]
    buffer.current_line_index = len(buffer.lines) - 1
    return (text, buffer)


NUMBER_REGEX = re.compile("[1-9][0-9]*")


def parse_number(text: str) -> Optional[Tuple[str, int]]:
    number_match = NUMBER_REGEX.match(text)
    if number_match is not None:
        return (text[number_match.end():], int(number_match.group()))
    else:
        return None


def parse_address(buffer: Buffer, text: str) -> Optional[Tuple[str, int]]:
    # If there are no lines in buffer.
    if buffer.current_line_index is None:
        return None
    number_match = parse_number(text)
    if number_match is not None:
        return (number_match[0], number_match[1] - 1)
    elif text.startswith("+"):
        number_match = parse_number(text[1:])
        if number_match is not None:
            return (number_match[0],
                    number_match[1] + buffer.current_line_index)
        else:
            return (text[1:], buffer.current_line_index + 1)
    elif text.startswith("-"):
        number_match = parse_number(text[1:])
        if number_match is not None:
            return (number_match[0],
                    number_match[1] - buffer.current_line_index)
        else:
            return (text[1:], buffer.current_line_index - 1)
    elif text.startswith("."):
        return (text[1:], buffer.current_line_index)
    elif text.startswith("$"):
        return (text[1:], len(buffer.lines) - 1)
    else:
        return None
