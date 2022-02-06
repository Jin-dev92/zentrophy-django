from django.db import models


# from django.contrib.auth.models import AbstractUser

# from util.models import TimeStampModel


class Member(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=100)  # 아이디의 역할을 함.
    # password = models.CharField(max_length=100)
    number = models.CharField(max_length=20, blank=True)  # 개인일 경우 생년월일, 사업자인경우 사업자 번호
    address = models.CharField(max_length=200, blank=True)
    address_detail = models.CharField(max_length=200, blank=True)
    zipCode = models.CharField(max_length=20, blank=True)
    is_business = models.BooleanField(default=False)
