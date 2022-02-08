from django.db import models

from order.constant import OrderState
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey('member.Member',
                              on_delete=models.SET_NULL,
                              null=True)
    payment_info = models.JSONField(null=True)
    subside = models.IntegerField(default=0)
    extra_subside = models.ManyToManyField('order.ExtraSubside')
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        return str(self.id)

    def order_change_state(self, state: OrderState):
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
