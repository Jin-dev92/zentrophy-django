from django.db import models


class PostType(models.IntegerChoices):
    FAQ = 0  # FAQ
    NOTICE = 1  # 공지사항
