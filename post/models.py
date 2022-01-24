from django.db import models
from post.constant import PostType
from util.models import TimeStampModel


class Post(TimeStampModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    post_type = models.PositiveSmallIntegerField(default=PostType.NOTICE)
