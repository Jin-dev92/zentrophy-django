from django.db import models

from conf.settings import LICENSE_NUMBER_LENGTH
from history.constant import RefundStatus, AfterServiceStatus, RefundMethod, AfterServiceCategory
from placement.models import Placement
from product.models import ProductOptions
from util.models import TimeStampModel, SoftDeleteModel


class RefundLocation(TimeStampModel):
    post_code = models.CharField(max_length=10, null=True)
    address_1 = models.CharField(max_length=200, null=True)
    address_2 = models.CharField(max_length=200, null=True)
    address_3 = models.CharField(max_length=200, null=True)


class Refund(TimeStampModel, SoftDeleteModel):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, null=True)
    reject_reason = models.CharField(max_length=200, null=True)
    refund_location = models.OneToOneField('history.RefundLocation', on_delete=models.CASCADE, null=True)
    method = models.PositiveSmallIntegerField(default=RefundMethod.RECALL_REQUEST)
    status = models.PositiveSmallIntegerField(default=RefundStatus.WAITING)


class AfterService(TimeStampModel, SoftDeleteModel):
    user = models.ForeignKey('member.User', on_delete=models.CASCADE, null=True)
    place = models.ForeignKey(Placement, on_delete=models.CASCADE)
    vehicle_license = models.CharField(max_length=20, null=True)
    registration_number = models.CharField(max_length=LICENSE_NUMBER_LENGTH, unique=True)
    status = models.PositiveSmallIntegerField(default=AfterServiceStatus.APPLY_WAITING)
    reservation_date = models.DateTimeField(null=True)
    detail = models.TextField(blank=True)
    category = models.PositiveSmallIntegerField(default=AfterServiceCategory.ETC)


class Warranty(TimeStampModel, SoftDeleteModel):
    name = models.CharField(max_length=100, blank=True)
    validity = models.DateTimeField(null=True)
    is_warranty = models.BooleanField(default=True, help_text="보증 범위 적용 유무")


class Cart(TimeStampModel):
    product_options = models.OneToOneField(ProductOptions, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.product_options.option_name + "//" + str(self.amount) + self.owner.email


class PrevEstimate(TimeStampModel):
    battery_user_avg_fee = models.FloatField(default=0, help_text="배터리 사용자 평균 사용 요금")
    consume_user_avg_fee = models.FloatField(default=0, help_text="소모품 사용자 평균 사용 요금")
    user_avg_fuel = models.FloatField(default=0, help_text="사용자 평균 전비")
    gasoline_calc = models.FloatField(default=0, help_text="가솔린 계수")
    battery_fee = models.FloatField(default=0, help_text="기본 배터리 요금")

    def __str__(self):
        return str(self.battery_user_avg_fee)