from email.policy import default

from django.db import models
from product.constant import ProductLabel
from product.schema import ProductDescription, VehicleColor, ProductOptions


class ProductDisplayLine(models.Model):  # 상품 진열 라인
    display_line_no = models.AutoField(primary_key=True)
    display_line_name = models.CharField(max_length=20, null=False)


class VehicleSubsidy(models.Model):
    subsidy_no = models.AutoField(primary_key=True)
    subsidy_name = models.CharField(max_length=100)
    subsidy_amount = models.IntegerField(default=0)


class Product(models.Model):
    product_no = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = ProductLabel
    # product_options = List<ProductOptions> # 리스트화
    is_display = models.BooleanField(default=False)
    display_line = models.ForeignKey(ProductDisplayLine, on_delete=models.SET_NULL, null=True)
    is_refundable = models.BooleanField(default=False)
    description = ProductDescription

    # file_url = models.FileField()
    def toggle_display(self):  # 필요없을거같긴함
        self.is_display = not self.is_display

    def push_product_options(self, options: ProductOptions):
        self.product_options = options

    def remove_product_options(self, options: ProductOptions):
        self.product_options = options
        # description = models.TextField(null=True, blank=True)  # 묶으면 좋을듯?
    # shipping_instructions = models.TextField(null=True, blank=True)
    # product_instructions = models.TextField(null=True, blank=True)


class Vehicle(models.Model):
    vehicle_no = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    subsidy = models.IntegerField(default=0)  # 보조금
    extra_subsidy = models.IntegerField(default=0)  # 추가 보조금 선택 가능하게 해야됨.
    is_display = models.BooleanField(default=False)
    color = VehicleColor # todo 리스트

    # file_url
    def toggle_display(self):
        self.is_display = not self.is_display
