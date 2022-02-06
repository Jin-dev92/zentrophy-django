from django.db import models

from member.models import Member
from order.constant import OrderState
from product.models import Product, Vehicle
from util.models import TimeStampModel


class Order(TimeStampModel):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(Member,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name='order_owner')  # 주문자
    product = models.ManyToManyField(Product)
    vehicle = models.ManyToManyField(Vehicle)
    extra_subside = models.ManyToManyField('order.ExtraSubside')
    amount = models.IntegerField(default=0, null=False, blank=False)
    state = models.PositiveSmallIntegerField(default=OrderState.ACCEPT_ORDER)

    def __str__(self):
        if self.product:
            return Product.objects.get(id=self.product).product_name
        elif self.vehicle:
            return Vehicle.objects.get(id=self.vehicle).vehicle_name

    def order_change_state(self, state: OrderState):
        self.state = state
        self.save()


class NecessaryDocumentFile(TimeStampModel):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to="order/%Y/%M",)
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
    description_1 = models.TextField(blank=True)  # 보조금 신청 시 필요 서류 및 안내
    description_2 = models.TextField(blank=True)  # 보조금 신청 시 주의 사항
