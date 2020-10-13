from buffer import Buffer
import re
from typing import Tuple, Optional
from copy import copy
from deepline_error import DeeplineError


class RangeError(DeeplineError):
    def __init__(self, message):
        super().__init__(f"Range error: {message}")


def parse_range(buffer: Buffer,
                text: str) -> Optional[Tuple[str, Tuple[int, int]]]:
    buffer = copy(buffer)  # Make sure we don't change the buffer.
    first_address, last_address = None, None

    # Parse the first address.
    address_match = parse_address(buffer, text)
    if address_match is not None:
        text = address_match[0]
        first_address = address_match[1]
        if address_match[1] >= len(buffer.lines):
            raise RangeError(
                f"First address: {first_address + 1}, is out of range of the buffer"
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
        last_address = first_address

    # Parse the last address.
    address_match = parse_address(buffer, text)
    if address_match is not None:
        text = address_match[0]
        last_address = address_match[1]
        if last_address >= len(buffer.lines):
            raise RangeError(
                f"Last address: {last_address}, is out of range of the buffer")

    if first_address is None and last_address is None:
        return None
    return (text,
            (first_address if first_address is not None else 0, last_address +
             1 if last_address is not None else len(buffer.lines)))


NUMBER_REGEX = re.compile("[1-9][0-9]*")


def parse_number(text: str) -> Optional[Tuple[str, int]]:
    number_match = NUMBER_REGEX.match(text)
    if number_match is not None:
        return (text[number_match.end():], int(number_match.group()))
    else:
        return None


def parse_address(buffer: Buffer, text: str) -> Optional[Tuple[str, int]]:
    # If there are no lines in buffer.
    number_match = parse_number(text)
    if number_match is not None:
        return (number_match[0], number_match[1] - 1)
    elif text.startswith("+"):
        if buffer.current_line_index is None:
            raise RangeError("No lines in buffer.")
        text = text[1:]
        number_match = parse_number(text)
        if number_match is not None:
            return (number_match[0],
                    number_match[1] + buffer.current_line_index)
        else:
            return (text[1:], buffer.current_line_index + 1)
    elif text.startswith("-"):
        if buffer.current_line_index is None:
            raise RangeError("No lines in buffer.")
        number_match = parse_number(text[1:])
        if number_match is not None:
            return (number_match[0],
                    number_match[1] - buffer.current_line_index)
        else:
            return (text[1:], buffer.current_line_index - 1)
    elif text.startswith("."):
        if buffer.current_line_index is None:
            raise RangeError("No lines in buffer.")
        return (text[1:], buffer.current_line_index)
    elif text.startswith("$"):
        if buffer.current_line_index is None:
            raise RangeError("No lines in buffer.")
        return (text[1:], len(buffer.lines) - 1)
    else:
        return None
