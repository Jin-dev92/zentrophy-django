from typing import Optional
from ninja import Schema


class ResponseDefaultHeader:
    def __init__(self, code: int, data: Optional[dict]):
        self.code = code
        # self.message = message
        if len(data) == 0:
            self.data = None
        else:
            self.data = data
        # self.data = len(data) == 0 ?? data

    class Schema(Schema):
        code: int
        data: Optional[dict] = None
