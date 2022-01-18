from django.db import models


class ProductLabel(models.IntegerChoices):
    HOT = 0
    NEW = 1
    SALE = 2
    BEST = 3


class ProductOptionsLabel(models.IntegerChoices):
    NORMAL = 0
    INPUT = 1
    NONE = 2
