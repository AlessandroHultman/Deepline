#!/usr/bin/python3
from command_parse import parse_and_run, create_command_list
from buffer import Buffer
from prompt_toolkit import PromptSession
from typing import Callable, Dict, List
from deepline_error import DeeplineError
import buffer_functions

PROMPT = "dl> "
WELCOME_MESSAGE = """Welcome to deepline

Type `h` to get more help.
"""

COMMANDS: Dict[str, Callable[[Buffer, List[str]],
                             None]] = create_command_list({
                                 "i":
                                 buffer_functions.insert,
                                 "a":
                                 buffer_functions.append,
                                 "p":
                                 buffer_functions.print,
                                 "r":
                                 buffer_functions.read,
                                 "w":
                                 buffer_functions.write,
                                 "q":
                                 buffer_functions.quit,
                             })


def run():
    print(WELCOME_MESSAGE)

    buffer = Buffer()  # Initialize buffer.

    prompt_session = PromptSession(PROMPT)  # Create prompt session.
    # Loop until EOF (End Of File).
    while True:
        # Issue the prompt.
        try:
            text = prompt_session.prompt()
        except EOFError:
            break

        # Try to parse the text and run an appropriate command.
        try:
            buffer = parse_and_run(COMMANDS, buffer, text)
        except DeeplineError as x:
            print(F"Deepline error: {x}")


if __name__ == "__main__":
    run()
