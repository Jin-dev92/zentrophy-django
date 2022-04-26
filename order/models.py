from django.db import models

from order.constant import OrderState
from product.models import ProductOptions, VehicleColor
from util.models import TimeStampModel, SoftDeleteModel


class OrderDetail(SoftDeleteModel):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)
    product_options = models.ForeignKey(ProductOptions, on_delete=models.SET_NULL, null=True, default=None)
    vehicle_color = models.ForeignKey(VehicleColor, on_delete=models.SET_NULL, null=True, default=None)
    amount = models.IntegerField(default=0)


class NecessaryDocumentFile(TimeStampModel):
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
    buy_list = models.JSONField(default=dict, null=True)
    subside = models.BooleanField(default=False)
    extra_subside = models.ManyToManyField(ExtraSubside)
    is_visited = models.BooleanField(default=False)
    total = models.IntegerField(default=0)
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        return str(self.id)

    # def order_change_state(self, state: OrderState):
    #     if self.state == state:
    #         raise ChangeOrderStateException
    #     if self.payment_type == PaymentType.VEHICLE:
    #         try:
    #             if self.state == OrderState.IS_COMPLETE:  # 배송 완료 했다가 다른 상태로 돌렸을 경우 배송 완료 되었을 때 생성되었던 사용자 모터사이클 리스트를 삭제해준다.
    #                 MemberOwnedVehicles.objects.get(order=self.objects.get(id=self.id)).delete()
    #             if state == OrderState.IS_COMPLETE:  # 사용자 보유 모터사이클 리스트에 객체를 생성하여 넣어준다.
    #                 goods_name = self.payment_info['GoodsName']
    #                 MemberOwnedVehicles.objects.create(
    #                     vehicle=Vehicle.objects.get(vehicle_name=goods_name),
    #                     order=self.objects.get(id=self.id),
    #                     owner=self.owner,
    #                 )
    #         except Exception as e:
    #             raise DataBaseORMException
    #
    #     self.state = state
    #     self.save()
    #
    # def sales_products(self):
    #     for detail in self.orderdetail_set.all():
    #         if self.payment_type == PaymentType.VEHICLE:
    #             if detail.vehicle_color.stock_count < detail.amount:
    #                 raise NotEnoughProductsException
    #             detail.vehicle_color.sale_count += detail.amount
    #             detail.vehicle_color.stock_count -= detail.amount
    #             detail.vehicle_color.save(update_fields=['sale_count', 'stock_count'])
    #         elif self.payment_type == PaymentType.PRODUCT:
    #             if detail.product_options.stock_count < detail.amount:
    #                 raise NotEnoughProductsException
    #             detail.product_options.sale_count += detail.amount
    #             detail.product_options.stock_count -= detail.amount
    #             detail.product_options.save(update_fields=['sale_count', 'stock_count'])
    #         else:
    #             pass
    #     pass
