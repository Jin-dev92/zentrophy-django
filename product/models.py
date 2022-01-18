# import orjson
from django.db import models
from product.constant import ProductLabel
from product.schema import ProductDescription, VehicleColor, ProductOptions


# class ProductDisplayLine(models.Model):  # 상품 진열 라인
#     display_line_no = models.AutoField(primary_key=True)
#     display_line_name = models.CharField(max_length=20, null=False)


class VehicleSubsidy(models.Model):
    subsidy_no = models.AutoField(primary_key=True)
    subsidy_name = models.CharField(max_length=100)
    subsidy_amount = models.IntegerField(default=0)


class Product(models.Model):
    product_no = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = models.IntegerField(choices=ProductLabel.choices, default=ProductLabel.NEW)
    product_options = models.TextField(blank=True)
    is_display = models.BooleanField(default=False)
    # display_line = models.TextField(null=True)
    # display_line = models.ForeignKey(ProductDisplayLine.display_line_no, on_delete=models.SET_NULL, null=True)
    is_refundable = models.BooleanField(default=False)
    description = models.TextField(blank=True)


class Vehicle(models.Model):
    vehicle_no = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    subsidy = models.IntegerField(default=0)  # 보조금 나중에 app으로 뺄것.
    extra_subsidy = models.IntegerField(default=0)  # 추가 보조금 선택 가능하게 해야됨.
    is_display = models.BooleanField(default=False)
    color = models.JSONField

    # color: models.TextField  # vehicleColor
    def toggle_display(self):
        self.is_display = not self.is_display
