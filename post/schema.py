# import datetime
import datetime

from ninja import Schema


# title = models.CharField(max_length=200)
# content = models.TextField()
# author = models.CharField(max_length=200)
# type = models.PositiveSmallIntegerField(choices=PostType.choices, default=PostType.NOTICE)
# is_created = models.DateTimeField(auto_now_add=True)  # 처음에 추가될때 생성된다.
# is_updated = models.DateTimeField(auto_now=True)  # 처음 추가 될때 생성이 되면서 데이터가 바뀔때 마다 같이 바뀌게된다.

class PostListSchema(Schema):
    id: int
    title: str
    content: str
    author: str
    type: int
    is_created: datetime
    is_updated: datetime


class PostInsertSchema(Schema):
    title: str
    content: str
    author: str  # @todo 나중에 user 와 연결 후 삭제
    type: int
