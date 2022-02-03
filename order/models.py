from django.db import models

from order.constant import OrderState
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField(null=False, blank=False)
    # owner = models.ForeignKey('auth.User')
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)
