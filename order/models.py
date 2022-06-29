from django.db import models

from member.models import User, OwnedVehicle
from order.constant import OrderState, DeliveryMethod, DeliveryCompany
from product.models import ProductOptions, VehicleColor
from util.models import TimeStampModel, SoftDeleteModel


class OrderDetail(SoftDeleteModel):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)
    product_options = models.ForeignKey(ProductOptions, on_delete=models.SET_NULL, null=True)
    vehicle_color = models.ForeignKey(VehicleColor, on_delete=models.SET_NULL, null=True)
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


class Order(TimeStampModel, SoftDeleteModel):
    owner = models.ForeignKey('member.User',
                              on_delete=models.CASCADE,
                              null=True)
    subside = models.BooleanField(default=False)
    extra_subside = models.ManyToManyField(ExtraSubside)
    is_visited = models.BooleanField(default=False)
    total = models.IntegerField(default=0)
    is_request_submit = models.BooleanField(default=False)
    discount_total = models.IntegerField(default=0)
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)
    customer_info = models.OneToOneField('order.CustomerInfo', on_delete=models.SET_NULL, null=True)
    order_location_info = models.OneToOneField('order.OrderLocationInfo', on_delete=models.SET_NULL, null=True)
    is_delivery = models.BooleanField(default=False, help_text="False = 출고 준비 중 , True = 배송 중", null=True)
    # 상품 배송 관련
    # product_option_input = models.TextField( help_text="상품이 입력형 일 경우에 텍스트 받는 필드.", null=True)
    product_delivery_info = models.OneToOneField('order.ProductDeliveryInfo', on_delete=models.CASCADE, null=True)
    # 모터사이클 배송 관련
    delivery_method = models.PositiveSmallIntegerField(default=DeliveryMethod.DEPEND_ON, null=True)
    delivery_to = models.OneToOneField('order.DeliveryTo', on_delete=models.SET_NULL, null=True)
    place_remote_pk = models.IntegerField(null=True, help_text="모터 사이클 직접 수령 시 수령 할 플레이스 입력")

    def __str__(self):
        return str(self.id)


class ProductDeliveryInfo(TimeStampModel):
    delivery_company = models.PositiveSmallIntegerField(null=True, help_text="택배사 이름")
    delivery_number = models.CharField(max_length=13, help_text="운송장 길이는 최대 13", null=True)


class DeliveryTo(TimeStampModel):
    post_code = models.CharField(max_length=10, null=True)
    address_1 = models.CharField(max_length=200, null=True)
    address_2 = models.CharField(max_length=200, null=True)
    address_3 = models.CharField(max_length=200, null=True)


class OrderedProductOptions(TimeStampModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product_options = models.ForeignKey(ProductOptions, on_delete=models.CASCADE, null=True)
    product_detail_input = models.TextField(null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.product_options.option_name


class OrderedVehicleColor(TimeStampModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    vehicle_color = models.ForeignKey(VehicleColor, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.vehicle_color.color_name


class CustomerInfo(TimeStampModel):
    name = models.CharField(max_length=100, null=True)
    birth = models.DateField(null=True)
    tel = models.CharField(max_length=20, null=True)
    email = models.EmailField(max_length=100, null=True)
    is_business = models.BooleanField(default=False)
    is_apply_subside = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class OrderLocationInfo(TimeStampModel):
    address_1 = models.CharField(max_length=100, null=True, help_text="우편 번호")
    address_2 = models.CharField(max_length=100, null=True)
    address_3 = models.CharField(max_length=100, null=True)
    detail = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.address_1) + str(self.address_2)


class DocumentFormat(TimeStampModel, SoftDeleteModel):
    file = models.FileField(upload_to="order/%Y/%M")


class Subscriptions(TimeStampModel, SoftDeleteModel):
    # owner = models.OneToOneField('member.User', on_delete=models.CASCADE, null=True)
    owned_vehicle = models.OneToOneField('member.OwnedVehicle', on_delete=models.CASCADE, null=True)
    merchant_uid = models.CharField(max_length=200, null=True, help_text="주문 번호")
    customer_uid = models.CharField(max_length=200, null=True, help_text="사용자 uid")
    imp_uid = models.CharField(max_length=200, null=True, help_text="결제 번호", unique=True)
    response_raw = models.JSONField(null=True, help_text="api 응답 원문")

    def __str__(self):
        return self.imp_uid


class Payment(TimeStampModel, SoftDeleteModel):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True)
    auth_result = models.JSONField(null=True)
    approval_result = models.JSONField(null=True)
