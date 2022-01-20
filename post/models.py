from django.db import models
from post.constant import PostType


class TimeStampModel(models.Model):
    is_created = models.DateTimeField(auto_now_add=True)  # 처음에 추가될때 생성된다.
    is_updated = models.DateTimeField(auto_now=True)  # 처음 추가 될때 생성이 되면서 데이터가 바뀔때 마다 같이 바뀌게된다.

    class Meta:
        abstract = True


class Post(TimeStampModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    post_type = models.IntegerField(choices=PostType.choices, default=PostType.NOTICE)
