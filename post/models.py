from django.db import models

from conf import settings
from util.models import TimeStampModel, SoftDeleteModel


class Post(TimeStampModel, SoftDeleteModel):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True


class FAQ(Post):
    category = models.ForeignKey('post.FAQCategory', on_delete=models.SET_NULL, null=True)


class FAQCategory(SoftDeleteModel):
    category_name = models.CharField(max_length=20)


class Notice(Post):
    pass
