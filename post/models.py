from django.db import models
from post.constant import PostType
from util.models import TimeStampModel


class Post(TimeStampModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    post_type = models.PositiveSmallIntegerField(default=PostType.NOTICE)

    def __str__(self):
        return self.title
