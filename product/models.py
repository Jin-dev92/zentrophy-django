from django.db import models
from colorfield.fields import ColorField
from product.constant import ProductLabel, ProductOptionsLabel
from sorl.thumbnail import ImageField
from util.models import TimeStampModel


class ProductDisplayLine(models.Model):  # 상품 진열 라인
    id = models.AutoField(primary_key=True)
    display_line_name = models.CharField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.display_line_name


class ProductImage(TimeStampModel):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    origin_image = ImageField(upload_to="product/%Y/%M", null=True)


class VehicleImage(TimeStampModel):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.CASCADE, null=True)
    origin_image = ImageField(upload_to="vehicle/%Y/%M", null=True)

    def __str__(self):
        return self.id


class ProductOptions(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, null=True)
    option_name = models.CharField(max_length=200, blank=True)
    stock_count = models.IntegerField(default=0)
    option_description = models.TextField(blank=True)
    is_apply = models.BooleanField(default=False)
    product_options_label = models.PositiveSmallIntegerField(
        default=ProductOptionsLabel.NORMAL,
        help_text="0 : 일반형, 1 : 입력형, 2: 해당 없음"
    )
    sale_count = models.IntegerField(default=0)

    def __str__(self):
        return self.option_name

    def sale(self):
        self.stock_count = self.stock_count - 1
        self.sale_count = self.sale_count + 1

    # class Meta:  # 이 옵션을 선언하면 해당 모델은 따로 테이블을 만들지 않는다.
    #     abstract = True


class VehicleColor(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.CASCADE, null=True)
    color_name = models.CharField(max_length=20, blank=True)
    stock_count = models.IntegerField(default=0)
    sale_count = models.IntegerField(default=0)
    hex_code = ColorField(default='#FFFFFF')
    on_sale = models.BooleanField(default=False)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name


class Product(TimeStampModel):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = models.PositiveSmallIntegerField(default=ProductLabel.NEW)  # 여러개 받을수 있게 해야함
    product_display_line = models.ManyToManyField('product.ProductDisplayLine')
    is_display = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=False)
    description = models.JSONField(default=dict)

    def __str__(self):
        return self.product_name


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    able_subsidy = models.BooleanField(default=False)
    able_extra_subsidy = models.BooleanField(default=False)
    is_display = models.BooleanField(default=False)

    def __str__(self):
        return self.vehicle_name
