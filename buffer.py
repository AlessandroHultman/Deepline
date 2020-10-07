from typing import Optional

class Buffer:
    def __init__(self):
        self.lines = []
        self.current_line_index: Optional[int] = None

    def current_line(self) -> Optional[str]:
        if self.current_line_index is not None:
            return self.lines[self.current_line_index]
        else:
            return None