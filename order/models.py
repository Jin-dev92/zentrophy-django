from django.db import models

from order.constant import OrderState
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('member.Member',
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
            raise Exception("변경하려는 주문 상태와 db 내 주문 상태가 같습니다.")
        # if self.is_vehicle:
        #     try:
        #         if self.state == OrderState.IS_COMPLETE:
        #             # @todo 배송 완료 했다가 다른 상태로 돌렸을 경우 배송 완료 되었을 때 생성되었던 사용자 모터사이클 리스트를 삭제해준다.
        #             # payment_info__product_info__product_id 와 조인을 때릴까?
        #             return None
        #         if state == OrderState.IS_COMPLETE:
        #             # @todo 사용자 보유 모터사이클 리스트에 객체를 생성하여 넣어준다.
        #             return None
        #     except Exception as e:
        #         raise Exception(e)

        self.state = state
        self.save()


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
