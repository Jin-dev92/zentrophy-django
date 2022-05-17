from django.db import models

from order.constant import OrderState
from product.models import ProductOptions, VehicleColor
from util.models import TimeStampModel, SoftDeleteModel


class OrderDetail(SoftDeleteModel):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)
    product_options = models.ForeignKey(ProductOptions, on_delete=models.SET_NULL, null=True, default=None)
    vehicle_color = models.ForeignKey(VehicleColor, on_delete=models.SET_NULL, null=True, default=None)
    amount = models.IntegerField(default=0)


class DocumentFile(TimeStampModel):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="order/%Y/%M", )
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)


class Subside(SoftDeleteModel):
    amount = models.IntegerField(default=0)


class ExtraSubside(SoftDeleteModel, TimeStampModel):
    name = models.CharField(max_length=100)
    amount = models.IntegerField(default=0)
    description_1 = models.TextField(blank=True, help_text="보조금 신청 시 필요 서류 및 안내")  # 보조금 신청 시 필요 서류 및 안내
    description_2 = models.TextField(blank=True, help_text="보조금 신청 시 주의 사항")  # 보조금 신청 시 주의 사항
    subside = models.ForeignKey('order.Subside', on_delete=models.CASCADE)


class IntegratedFeePlan(SoftDeleteModel):
    zentrophy_fee = models.IntegerField(default=0)
    battery_fee = models.IntegerField(default=0)


class Order(TimeStampModel, SoftDeleteModel):
    owner = models.ForeignKey('member.User',
                              on_delete=models.CASCADE,
                              null=True)
    ordered_product_options = models.ManyToManyField('order.OrderedProductOptions')
    ordered_vehicle_color = models.ManyToManyField('order.OrderedVehicleColor')
    subside = models.BooleanField(default=False)
    extra_subside = models.ManyToManyField(ExtraSubside)
    is_visited = models.BooleanField(default=False)
    total = models.IntegerField(default=0)
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        return str(self.id)

    def check_total(self):
        return


class OrderedProductOptions(TimeStampModel):
    product_options = models.ForeignKey(ProductOptions, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.product_options.option_name + self.amount


class OrderedVehicleColor(TimeStampModel):
    vehicle_color = models.ForeignKey(VehicleColor, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.vehicle_color.color_name + self.amount
