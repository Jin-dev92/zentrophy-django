from typing import Optional

from django.db import models

from conf.settings import LICENSE_NUMBER_LENGTH
from history.constant import RefundStatus, AfterServiceStatus, RefundMethod, AfterServiceCategory
from order.models import Order
from placement.models import Placement
from util.models import TimeStampModel


class History(TimeStampModel):
    id: models.AutoField(primary_key=True)

    class Meta:
        abstract = True


class Refund(History):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reject_reason = models.CharField(max_length=200, blank=True)
    method = models.PositiveSmallIntegerField(default=RefundMethod.RECALL_REQUEST)
    status = models.PositiveSmallIntegerField(default=RefundStatus.WAITING)


class AfterService(History):
    place = models.ForeignKey('placement.Placement', on_delete=models.CASCADE)
    vehicle = models.ForeignKey('member.MemberOwnedVehicles', on_delete=models.CASCADE, null=True)
    registration_number = models.CharField(max_length=LICENSE_NUMBER_LENGTH, unique=True)
    status = models.PositiveSmallIntegerField(default=AfterServiceStatus.APPLY_WAITING)
    reservation_date = models.DateTimeField(null=True)
    detail = models.TextField(blank=True)
    category = models.PositiveSmallIntegerField(default=AfterServiceCategory.ETC)


class IntegratedFeePlan(History):
    cumulative_usage = models.IntegerField(default=0)  # 누적 사용량
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class BatteryExchange(History):
    used_battery = models.FloatField(default=0.0)
    place = models.ForeignKey(Placement, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class Warranty(History):
    name = models.CharField(max_length=100, blank=True)
    validity = models.DateTimeField(null=True)
    is_warranty = models.BooleanField(default=True)
