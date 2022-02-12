from django.db import models

from conf.settings import LICENSE_NUMBER_LENGTH
from history.constant import RefundStatus, AfterServiceStatus
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
    reject_method = models.CharField(max_length=200, blank=True)
    status = models.PositiveSmallIntegerField(default=RefundStatus.WAITING)

    def change_status(self, status: RefundStatus):
        self.status = status
        self.save()

    def set_reject_reason(self, reject_reason: str):
        self.reject_reason = reject_reason
        self.save()


class AfterService(History):
    place = models.ForeignKey(Placement, on_delete=models.CASCADE)
    owner = models.ForeignKey('member.Member', on_delete=models.CASCADE, null=True)
    registration_number = models.CharField(max_length=LICENSE_NUMBER_LENGTH, unique=True)
    status = models.PositiveSmallIntegerField(default=AfterServiceStatus.APPLY_WAITING)


class IntegratedFeePlan(History):
    cumulative_usage = models.IntegerField(default=0)  # 누적 사용량
    order = models.ForeignKey(Order, on_delete=models.CASCADE)


class BatteryExchange(History):
    used_battery = models.FloatField(default=0.0)
    place = models.ForeignKey(Placement, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
