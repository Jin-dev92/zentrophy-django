# import orjson
from django.db import models
from product.constant import ProductLabel, ProductOptionsLabel


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, null=False)
    product_price = models.IntegerField(default=0)
    product_label = models.PositiveSmallIntegerField(choices=ProductLabel.choices, default=ProductLabel.NEW)
    is_display = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=False)
    description = models.JSONField


class Vehicle(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle_name = models.CharField(max_length=200)
    zero_to_fifty = models.IntegerField(default=0)
    max_speed = models.IntegerField(default=0)
    max_output = models.IntegerField(default=0)
    # subsidy = models.IntegerField(default=0)  # 보조금 나중에 app으로 뺄것.
    # extra_subsidy = models.IntegerField(default=0)  # 추가 보조금 선택 가능하게 해야됨.
    is_display = models.BooleanField(default=False)
    # vehicle_subsidy_id = models.OneToOneField(VehicleSubsidy,)
    # def toggle_display(self):
    #     self.is_display = not self.is_display


class VehicleSubsidy(models.Model):
    id = models.AutoField(primary_key=True)
    vehicle_id = models.OneToOneField(Vehicle, on_delete=models.CASCADE)
    subsidy_name = models.CharField(max_length=100)
    subsidy_amount = models.IntegerField(default=0)
    extra_subsidy = models.IntegerField(default=0)


class ProductDisplayLine(models.Model):  # 상품 진열 라인
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, default=None)
    display_line_name = models.CharField(max_length=20, null=False)


class ProductOptionsModel(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    option_name: models.CharField(max_length=200)
    stock_count = models.IntegerField(default=0)
    option_description = models.TextField(blank=True)
    is_apply = models.BooleanField(default=False)
    product_options_label = models.PositiveSmallIntegerField(
        choices=ProductOptionsLabel.choices,
        default=ProductOptionsLabel.NORMAL
    )

    class Meta:  # 이 옵션을 선언하면 해당 모델은 따로 테이블을 만들지 않는다.
        abstract = True


class VehicleColorModel(models.Model):
    id: models.AutoField(primary_key=True)
    vehicle_id: models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True)
    color_name: models.CharField(max_length=20)
    stock_count: models.IntegerField(default=0)
    hex_code: models.CharField(max_length=7)
    on_sale: models.BooleanField(default=False)
    price: models.IntegerField(default=0)

    class Meta:
        abstract: True
