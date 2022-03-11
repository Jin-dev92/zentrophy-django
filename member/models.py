from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser, Group

from conf.custom_exception import WrongBusinessNumberException, WrongBirthNumberException
from member.constant import CardCompany
from util.models import TimeStampModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, username, **kwargs):
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **self.parameters_validation_check(**kwargs)
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

    def parameters_validation_check(self, **kwargs):
        is_business = kwargs.get('is_business')
        for kwarg in kwargs:
            if kwarg == 'member_info_number':  # 멤버 번호 유효성 체크
                length = len(''.join(char for char in kwargs[kwarg] if char not in '-'))  # - 제거
                if is_business:
                    if length != 10:
                        raise WrongBusinessNumberException
                else:
                    if length != 8:
                        raise WrongBirthNumberException
        return kwargs


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=100)  # 아이디의 역할을 함.
    member_info_number = models.CharField(max_length=20, blank=True)  # 개인일 경우 생년월일, 사업자인경우 사업자 번호
    address = models.CharField(max_length=200, blank=True)
    address_detail = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    is_business = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    groups = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, default=None)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']


class MemberOwnedVehicles(TimeStampModel):
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey('order.Order', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE)
    license_code = models.CharField(max_length=50, default=None)
    battery_left = models.IntegerField(default=-1)  # -1의 경우 사용 불가.


class PaymentMethod(TimeStampModel):
    name = models.CharField(max_length=100)  # 결제 수단 별명
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE)
    card = models.ForeignKey('member.Card', on_delete=models.CASCADE, null=True)
    favorite = models.BooleanField(default=False)


class Card(models.Model):
    card_number = models.CharField(max_length=16, null=True)
    card_company = models.CharField(max_length=10, choices=CardCompany.choices, default=CardCompany.ETC)
    validate_date = models.DateField(null=True)
    security_code = models.CharField(max_length=4, null=True)
