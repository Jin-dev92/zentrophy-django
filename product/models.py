from colorfield.fields import ColorField
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from sorl.thumbnail import ImageField

from product.constant import ProductOptionsLabel
from util.models import TimeStampModel, SoftDeleteModel, FileExistModel


class ProductDisplayLine(SoftDeleteModel):  # 상품 진열 라인
    display_line_name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.display_line_name


class ProductImage(TimeStampModel, SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    origin_image = ImageField(upload_to="product/%Y/%M", null=True)


class VehicleImage(TimeStampModel, SoftDeleteModel, FileExistModel):
    id = models.AutoField(primary_key=True)
    vehicle_color = models.ForeignKey('product.VehicleColor', on_delete=models.CASCADE, null=True)
    origin_image = ImageField(upload_to="vehicle/%Y/%M", null=True)

    def __str__(self):
        return str(self.origin_image)


class ProductOptions(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, null=True)
    option_name = models.CharField(max_length=200, blank=True)
    option_price = models.IntegerField(default=0)
    option_description = models.TextField(blank=True, help_text="옵션 설명")
    is_apply = models.BooleanField(default=False, help_text="옵션 적용 여부")
    product_options_label = models.PositiveSmallIntegerField(
        default=ProductOptionsLabel.NORMAL,
        help_text="0 : 일반형, 1 : 입력형, 2: 해당 없음"
    )
    sale_count = models.IntegerField(default=0, help_text="판매량")
    stock_count = models.IntegerField(default=0, help_text="재고 수량")

    def __str__(self):
        return self.option_name


class VehicleColor(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.CASCADE, null=True)
    color_name = models.CharField(max_length=20, blank=True)
    stock_count = models.IntegerField(default=0, help_text="재고 수량")
    sale_count = models.IntegerField(default=0, help_text="판매량")
    hex_code = ColorField(default='#FFFFFF')
    on_sale = models.BooleanField(default=False, help_text="판매 유무")
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name


class Product(TimeStampModel, SoftDeleteModel, FileExistModel):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = models.PositiveSmallIntegerField(null=True)
    product_display_line = models.ManyToManyField('product.ProductDisplayLine', help_text="전시 라인 설정, 최대 2개")
    is_display = models.BooleanField(default=False, help_text="전시 유무")
    is_refundable = models.BooleanField(default=False, help_text="환불 가능 유무")
    product_description = models.TextField(blank=True, default="", help_text="상품 설명")
    shipping_instructions = models.TextField(blank=True, default="", help_text="배송 안내")
    refund_instructions = models.TextField(blank=True, default="", help_text="환불 안내")

    def __str__(self):
        return self.product_name


class Vehicle(SoftDeleteModel):
    id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    able_subsidy = models.BooleanField(default=False, help_text="기본 보조금 적용 여부")
    able_extra_subsidy = models.BooleanField(default=False, help_text="추가 보조금 적용 여부")
    is_display = models.BooleanField(default=False)

    def __str__(self):
        return self.vehicle_name


class SubscriptionProduct(TimeStampModel, SoftDeleteModel):  # 정기 구독 상품
    name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    description = models.TextField(null=True)
    merchant_uid = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name + self.merchant_uid
