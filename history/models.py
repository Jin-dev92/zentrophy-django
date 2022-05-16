from django.db import models

from conf.settings import LICENSE_NUMBER_LENGTH
from history.constant import RefundStatus, AfterServiceStatus, RefundMethod, AfterServiceCategory
from order.models import Order
from product.models import Product
from util.models import TimeStampModel, SoftDeleteModel


class Refund(TimeStampModel, SoftDeleteModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reject_reason = models.CharField(max_length=200, blank=True)
    method = models.PositiveSmallIntegerField(default=RefundMethod.RECALL_REQUEST)
    status = models.PositiveSmallIntegerField(default=RefundStatus.WAITING)


class AfterService(TimeStampModel, SoftDeleteModel):
    user = models.ForeignKey('member.User', on_delete=models.CASCADE, null=True)
    place = models.ForeignKey('placement.Placement', on_delete=models.CASCADE)
    owned_vehicle = models.ForeignKey('member.MemberOwnedVehicles', on_delete=models.CASCADE, null=True)
    registration_number = models.CharField(max_length=LICENSE_NUMBER_LENGTH, unique=True)
    status = models.PositiveSmallIntegerField(default=AfterServiceStatus.APPLY_WAITING)
    reservation_date = models.DateTimeField(null=True)
    detail = models.TextField(blank=True)
    category = models.PositiveSmallIntegerField(default=AfterServiceCategory.ETC)


# class BatteryExchange(TimeStampModel, SoftDeleteModel):
#     place = models.ForeignKey(Placement, on_delete=models.CASCADE)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     member_vehicle = models.ForeignKey(MemberOwnedVehicles, on_delete=models.CASCADE, null=True)
#     fee_plan = models.ForeignKey('order.IntegratedFeePlan', on_delete=models.SET_NULL, null=True)
#     used_battery = models.FloatField(default=0.0)


class Warranty(TimeStampModel, SoftDeleteModel):
    name = models.CharField(max_length=100, blank=True)
    validity = models.DateTimeField(null=True)
    is_warranty = models.BooleanField(default=True)


class Cart(TimeStampModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.product.product_name + "//" + str(self.amount) + self.owner.email
