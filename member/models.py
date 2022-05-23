import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models

from conf import settings
from conf.custom_exception import AlreadyExistsException, FormatNotSupportedException
# from member.constant import CardCompany
from util.models import TimeStampModel, SoftDeleteModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, username, **kwargs):
        if len(User.objects.filter(email=email)) > 0:
            raise AlreadyExistsException
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        super_user = self.create_user(
            email=self.normalize_email(email),
            username="admin",
            password=password,
        )
        super_user.is_admin = True
        super_user.is_superuser = True
        super_user.is_staff = True
        super_user.save(using=self._db)

        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=100)  # 아이디의 역할을 함.
    phone_number = models.CharField(unique=True, max_length=12, null=True)
    address = models.CharField(max_length=200, blank=True)
    address_detail = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    access_token = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    groups = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, default=None)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']


class MemberOwnedVehicles(TimeStampModel, SoftDeleteModel):
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE)
    license_code = models.CharField(max_length=50, default=None)
    battery_left = models.IntegerField(default=-1)  # -1의 경우 사용 불가.


class PaymentMethod(TimeStampModel, SoftDeleteModel):
    name = models.CharField(max_length=100)  # 결제 수단 별명
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE)
    card = models.ForeignKey('member.Card', on_delete=models.CASCADE, null=True)
    favorite = models.BooleanField(default=False)


class Card(SoftDeleteModel):
    card_number = models.CharField(max_length=16, null=True)
    user_name = models.CharField(max_length=100, null=True)
    validate_date = models.CharField(max_length=4, null=True)
    cvc = models.CharField(max_length=4, null=True)

    def __str__(self):
        return self.card_number

    def format(self):
        if len(self.card_number) != 16:
            raise FormatNotSupportedException
        if len(self.validate_date) != 4:
            raise FormatNotSupportedException
        if len(self.cvc) != 3:
            raise FormatNotSupportedException
        validate_month = int(self.validate_date[0:2])
        validate_year = int(settings.YEAR_TWO_DIGIT + self.validate_date[2:4])
        if validate_month < 1 or validate_month > 12:
            raise FormatNotSupportedException
        if validate_year < datetime.datetime.now().year:
            raise FormatNotSupportedException
