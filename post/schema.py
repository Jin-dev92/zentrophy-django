import datetime

from ninja import Schema


class PostListSchema(Schema):
    id: int
    title: str
    content: str
    author: str
    post_type: int
    is_created: datetime.datetime
    is_updated: datetime.datetime


class PostInsertSchema(Schema):
    title: str
    content: str
    author: str  # @todo 나중에 user 와 연결 후 삭제
    type: int


class PostModifySchema(Schema):
    title: str
    content: str
    author: str  # @todo 나중에 user 와 연결 후 삭제
