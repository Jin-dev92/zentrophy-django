from typing import Optional


class ResponseDefaultHeader:
    def __init__(self):
        self.code = None
        self.message = None
        self.data = None

    def build(self, code: int, message: Optional[str], data: Optional[list or dict]):
        self.code = code
        self.message = message
        self.data = data
