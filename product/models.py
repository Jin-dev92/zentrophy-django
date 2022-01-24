import random

from django.db import models
from product.constant import ProductLabel, ProductOptionsLabel
from sorl.thumbnail import ImageField
from util.models import TimeStampModel


class ProductDisplayLine(models.Model):  # 상품 진열 라인
    id = models.AutoField(primary_key=True)
    display_line_name = models.CharField(max_length=20, null=False)


class ProductImage(TimeStampModel):
    id = models.AutoField(primary_key=True)
    product_options_id = models.ForeignKey('product.ProductOptions', on_delete=models.CASCADE, null=True)
    origin_image = ImageField(upload_to="thumb/%Y/%M/%D/%HH/%MM/%SS" + str(int(random.random() * 100000)))

    def upload_to_server(self):
        print(self.origin_image)

    def get_image_name(self):
        return self.origin_image.name


class ProductOptions(models.Model):
    id = models.AutoField(primary_key=True)
    option_name: models.CharField(max_length=200)
    stock_count = models.IntegerField(default=0)
    option_description = models.TextField(blank=True)
    is_apply = models.BooleanField(default=False)
    product_options_label = models.PositiveSmallIntegerField(
        default=ProductOptionsLabel.NORMAL,
        help_text="0 : 일반형, 1 : 입력형, 2: 해당 없음"
    )
    sale_count = models.IntegerField(default=0)

    def sale(self):
        self.stock_count = self.stock_count - 1
        self.sale_count = self.sale_count + 1

    # class Meta:  # 이 옵션을 선언하면 해당 모델은 따로 테이블을 만들지 않는다.
    #     abstract = True


class VehicleColor(models.Model):
    id: models.AutoField(primary_key=True)
    vehicle_id = models.ForeignKey('product.Vehicle', on_delete=models.CASCADE, null=True)
    color_name: models.CharField(max_length=20)
    stock_count: models.IntegerField(default=0)
    hex_code: models.CharField(max_length=7)
    on_sale: models.BooleanField(default=False)
    price: models.IntegerField(default=0)


class Product(TimeStampModel):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = models.PositiveSmallIntegerField(default=ProductLabel.NEW)
    # product_display_line = models.ForeignKey('product.ProductDisplayLine', default=None, on_delete=models.SET_NULL,
    #                                          null=True)
    # product_options = models.ForeignKey('product.ProductOptions', on_delete=models.SET_NULL, null=True)

    is_display = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=False)
    description = models.JSONField(default=dict)


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    able_subsidy = models.BooleanField(default=False)
    able_extra_subsidy = models.BooleanField(default=False)
    is_display = models.BooleanField(default=False)
