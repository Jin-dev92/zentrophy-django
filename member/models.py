from django.db import models
from util.models import TimeStampModel


class Member(TimeStampModel):
    # id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=100)  # 아이디의 역할을 함.
    member_info_number = models.CharField(max_length=20, blank=True)  # 개인일 경우 생년월일, 사업자인경우 사업자 번호
    address = models.CharField(max_length=200, blank=True)
    address_detail = models.CharField(max_length=200, blank=True)
    zipCode = models.CharField(max_length=20, blank=True)
    is_business = models.BooleanField(default=False)


class MemberOwnedVehicles(TimeStampModel):
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True)
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey('member.Member', on_delete=models.CASCADE)
    recent_exchange_history = models.ForeignKey('history.BatteryExchange', on_delete=models.SET_NULL, null=True,
                                                default=None)
    license_code = models.CharField(max_length=20)
    battery_left = models.IntegerField(default=-1)  # -1의 경우 사용 불가.
