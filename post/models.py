import time
from enum import Enum

from django.db import models


class PostType(Enum):
    FAQ = 0,
    NOTICE = 1,


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=200)
    type = PostType
    is_created = models.DateTimeField(default=time.localtime())
