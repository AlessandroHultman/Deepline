from typing import Optional


class Buffer:
    def __init__(self):
        self.lines: list[str] = []
        self.current_line_index: Optional[int] = None
        self.current_file: Optional[str] = None
        self.history: list(Buffer) = []
        self.undone: list(Buffer) = []

    def current_line(self) -> Optional[str]:
        if self.current_line_index is not None:
            return self.lines[self.current_line_index]
        else:
            return None
