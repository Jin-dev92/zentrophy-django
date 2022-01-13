from django.db import models

from post.constant import PostType


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    post_type = PostType
    is_created = models.DateTimeField(auto_created=True)
