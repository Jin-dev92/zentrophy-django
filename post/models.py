from django.db import models
from util.models import TimeStampModel


class Post(TimeStampModel):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    class Meta:
        abstract = True


class FAQ(Post):
    category = models.ForeignKey('post.FAQCategory', on_delete=models.SET_NULL, null=True)


class FAQCategory(models.Model):
    category_name = models.CharField(max_length=20)


class Notice(Post):
    pass
