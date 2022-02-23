from django.db import models

from member.models import MemberOwnedVehicles
from order.constant import OrderState, ErrorMessage
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('member.User',
                              on_delete=models.CASCADE,
                              null=True)
    payment_info = models.JSONField(null=True)
    is_vehicle = models.BooleanField(default=False)
    is_able_subside = models.BooleanField(default=False)
    extra_subside = models.ManyToManyField('order.ExtraSubside')
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        return str(self.id)

    def order_change_state(self, state: OrderState):
        if self.state == state:
            raise Exception(ErrorMessage.CANT_CHANGE_ORDER_STATE)
        # if self.is_vehicle:
        #     try:
        #         if self.state == OrderState.IS_COMPLETE:  # 배송 완료 했다가 다른 상태로 돌렸을 경우 배송 완료 되었을 때 생성되었던 사용자 모터사이클 리스트를 삭제해준다.
        #             return None
        #             # qs = MemberOwnedVehicles.objects.filter(order=Order.objects.get(id=self.id)).delete()
        #             # assert qs
        #         if state == OrderState.IS_COMPLETE:  # 사용자 보유 모터사이클 리스트에 객체를 생성하여 넣어준다.
        #             qs = MemberOwnedVehicles.objects.create(
        #                 # order=self.id,
        #                 vehicle=self.payment_info,  # @todo 나중에 제대로 넣어야함.
        #                 owner=self.owner,
        #                 license_code=self.payment_info['license_code'],  # @todo 나중에 제대로 넣어야함.
        #             )
        #             assert qs
        #     except Exception as e:
        #         raise Exception(e)

        self.state = state
        self.save()

    # def sales_products(self):
    #     # 판매 후 불러 오는 함수 재고량 -1 , 판매량 +1
    #     pk = self.payment_info['product_id']
    #     if pk is None:
    #         pk = 1  # todo 나중에 바꿀 것 테스트 용 코드
    #     if self.is_vehicle:
    #         model = Vehicle
    #     else:
    #         model = ProductOptions
    #         stock_count = model.objects.get(id=pk).stock_count
    #         sale_count = model.objects.get(id=pk).sale_count
    #         if stock_count == 0:
    #             raise ValueError(ErrorMessage.CANT_SALE_STOCK_COUNT_IS_ZERO)
    #         stock_count = stock_count - 1
    #         sale_count = sale_count + 1
    #         model.save()
    #     return None


class NecessaryDocumentFile(TimeStampModel):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="order/%Y/%M", )
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name="order_files")


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
