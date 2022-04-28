from typing import List
from ninja import Schema


class ResponseDefaultHeader:
    def __init__(self, code: int, data: List[dict] = None, message: str = None):
        self.code = code
        self.message = message
        self.data = data
        # if data is None:
        #     self.data = None
        # else:
        #     self.data = data
        # self.data = len(data) == 0 ?? data

    class Schema(Schema):
        code: int
        message: str = None
        data: List[dict] = None


# class CommonBase64FileSchema(Schema):
#     base64_encoded: str


# class DefaultResponse(Schema)