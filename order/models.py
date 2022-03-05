from django.db import models

from conf import settings
from member.models import MemberOwnedVehicles, PaymentMethod
from order.constant import OrderState, PaymentType
from util.exception.constant import ErrorMessage
from product.models import Vehicle, ProductOptions, VehicleColor
from util.exception.exception import MustHaveSplitWordException, NotEnoughProductsException
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('member.User',
                              on_delete=models.CASCADE,
                              null=True)
    payment_type = models.PositiveSmallIntegerField(default=0)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    payment_info = models.JSONField(null=True)
    is_able_subside = models.BooleanField(default=False)
    extra_subside = models.ManyToManyField('order.ExtraSubside')
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        return str(self.id)

    def order_change_state(self, state: OrderState):
        if self.state == state:
            raise Exception(ErrorMessage.CANT_CHANGE_ORDER_STATE)
        if self.payment_type == PaymentType.VEHICLE:
            try:
                if self.state == OrderState.IS_COMPLETE:  # 배송 완료 했다가 다른 상태로 돌렸을 경우 배송 완료 되었을 때 생성되었던 사용자 모터사이클 리스트를 삭제해준다.
                    MemberOwnedVehicles.objects.get(order=self.objects.get(id=self.id)).delete()
                if state == OrderState.IS_COMPLETE:  # 사용자 보유 모터사이클 리스트에 객체를 생성하여 넣어준다.
                    goods_name = self.payment_info['GoodsName']
                    MemberOwnedVehicles.objects.create(
                        vehicle=Vehicle.objects.get(vehicle_name=goods_name),
                        order=self.objects.get(id=self.id),
                        owner=self.owner,
                    )
            except Exception as e:
                raise Exception(e)

        self.state = state
        self.save()

    def sales_products(self):
        # 판매 후 불러 오는 함수 재고량 -1 , 판매량 +1
        goods: str = self.payment_info['GoodsName']
        if settings.OPTION_SPLIT not in goods:
            raise MustHaveSplitWordException
        goods_name = goods.split(settings.OPTION_SPLIT)[0]
        extra = goods.split(settings.OPTION_SPLIT)[1]

        if self.payment_type == PaymentType.VEHICLE:
            obj = VehicleColor.objects.get(vehicle__vehicle_name=goods_name, color_name=extra)
        elif self.payment_type == PaymentType.PRODUCT:
            obj = ProductOptions.objects.get(product__product_name=goods_name, option_name=extra)
            if obj.stock_count == 0:
                raise NotEnoughProductsException
            obj.sale_count += 1
            obj.stock_count -= 1
        else:
            pass
            # raise ValueError(ErrorMessage.CANT_APPLY_PERIOD_PAYMENT)

        obj.save()


class NecessaryDocumentFile(TimeStampModel):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="order/%Y/%M", )
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)


class Subside(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(default=0)

    class Meta:
        abstract = True


class ExtraSubside(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    amount = models.IntegerField(default=0)
    description_1 = models.TextField(blank=True, help_text="보조금 신청 시 필요 서류 및 안내")  # 보조금 신청 시 필요 서류 및 안내
    description_2 = models.TextField(blank=True, help_text="보조금 신청 시 주의 사항")  # 보조금 신청 시 주의 사항


class IntegratedFeePlan(models.Model):
    zentrophy_fee = models.IntegerField(default=0)
    battery_fee = models.IntegerField(default=0)
