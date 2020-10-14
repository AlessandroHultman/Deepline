from argparse import ArgumentParser
import buffer_functions
import inspect
import shlex
import typing
from typing import Optional, Dict, List, Callable, Tuple, Set
from buffer import Buffer
from line_range import parse_range
from deepline_error import DeeplineError

ALLOWED_ARG_TYPES: Set = {str, int, float}


def create_command_list(
    commands: Dict[str, Callable]
) -> Dict[str, Callable[[Buffer, List[str]], None]]:
    def help(_: Buffer):
        "Print help message for all commands."
        print("Availlable commands:\n")
        for name, function in commands.items():
            print(f"{name}, {function.__name__}",
                  ",  " +
                  function.__doc__ if function.__doc__ is not None else "",
                  sep="")

    assert "h" not in commands, "The command name 'h' is reserved for the help command."
    commands["h"] = help

    return {name: create_command(f) for (name, f) in commands.items()}


def create_command(function: Callable[..., None]):
    func_name = function.__name__
    description = function.__doc__
    signature = inspect.signature(function)

    # Make sure the first argument is a buffer.
    try:
        assert list(signature.parameters.values())[0].annotation is Buffer
    except (AssertionError, IndexError):
        raise DeeplineError(
            f"The first parameter of function {func_name} must have the type buffer."
        )

    # Create an argument parser.
    argparser = ArgumentParser(prog=func_name, description=description)

    # Create all arguments.

    # A set of the one letter optional arguments like "-f" so we can make sure we avoid any duplicates.
    optional_short_argnames: Set = set()
    for parameter in list(signature.parameters.values())[1:]:
        parameter_type = parameter.annotation

        # Check wether the parameter is Optional.
        _type_args = typing.get_args(parameter_type)
        if typing.get_origin(parameter_type) is typing.Union and len(
                _type_args) == 2 and isinstance(None, _type_args[1]):
            parameter_type = _type_args[0]
            is_optional = True
        else:
            is_optional = False
        assert parameter_type in ALLOWED_ARG_TYPES, f"Type {parameter_type} in function {func_name} is not allowed as the type of an argument."

        # Check if we should make an optional argument.
        if parameter.default is not inspect.Parameter.empty or is_optional:
            # A list of short and long names for the argument.
            argnames = []
            short_argname = f"-{parameter.name[0]}"
            # Make sure this short argname has not been used before.
            if short_argname not in optional_short_argnames:
                optional_short_argnames.add(short_argname)
                argnames.append(short_argname)
            long_argname = f"--{parameter.name}"
            argnames.append(long_argname)

            argparser.add_argument(
                *argnames,
                type=parameter_type,
                default=parameter.default
                if parameter.default is not inspect.Parameter.empty else None)
        else:
            # This is a positional argument.
            argparser.add_argument(parameter.name, type=parameter_type)

    def command(buffer: Buffer, args: List[str]) -> None:
        # Parse the arguments and catch SystemExit in case of a failure.
        try:
            parsed_args = argparser.parse_args(args)
        except SystemExit:
            pass
        else:
            # Execute the function with the parsed arguments.
            function(buffer, **vars(parsed_args))

    return command


def parse_and_run(commands: Dict[str, Callable[[Buffer, List[str]], None]],
                  buffer: Buffer, text: str) -> Buffer:
    # Try to parse a range before the command.
    parsed_range = parse_range(buffer, text)
    if parsed_range is not None:
        text, (start, end) = parsed_range
        range_buffer = Buffer()
        range_buffer.lines = buffer.lines[start:end].copy()
        range_buffer.current_line_index = len(range_buffer.lines) - 1
        range_buffer.first_line_number += start
        # If no text was supplied after the range, only print and move current line to the last line in the range.
        if text.strip() == "":
            buffer_functions.print(range_buffer)
            if end > 0:
                buffer.current_line_index = end - 1
            return buffer

        range_buffer = parse_and_run(commands, range_buffer, text)
        # Assign the possibly changed lines in the range to the lines in the buffer.
        buffer.lines[start:end] = range_buffer.lines
        # If buffer has shrinked beyond current line, set current line to last line.
        if buffer.current_line_index is None or buffer.current_line_index >= len(
                buffer.lines):
            buffer.current_line_index = len(buffer.lines) - 1 if len(
                buffer.lines) > 0 else None
        return buffer

    # Split up text to args.
    args: List[str] = shlex.split(text)
    try:
        command_name = args[0]
    except IndexError:
        raise DeeplineError("No command specified")
    args = args[1:]

    # Find the appropriate command.
    try:
        command_function = commands[command_name]
    except KeyError:
        raise DeeplineError(f"{command_name}: command not found")

    command_function(buffer, args)
    return buffer
