# import datetime

from ninja import Schema


class PostListScheme(Schema):
    id: int
    title: str
    content: str
    author: str
