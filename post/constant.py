from django.db import models


class PostType(models.TextChoices):
    FAQ = 0  # FAQ
    NOTICE = 1  # 공지사항
