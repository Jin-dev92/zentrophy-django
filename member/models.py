from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from util.models import TimeStampModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, username, **kwargs):
        if not email:
            raise ValueError('이메일이 필요합니다.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username):
        super_user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        super_user.is_admin = True
        super_user.is_superuser = True
        super_user.is_staff = True
        super_user.save(using=self._db)
        return super_user

    def validator(self):
        return True


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=100)  # 아이디의 역할을 함.
    member_info_number = models.CharField(max_length=20, blank=True)  # 개인일 경우 생년월일, 사업자인경우 사업자 번호
    address = models.CharField(max_length=200, blank=True)
    address_detail = models.CharField(max_length=200, blank=True)
    zipCode = models.CharField(max_length=20, blank=True)
    is_business = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']


class MemberOwnedVehicles(TimeStampModel):
    vehicle = models.ForeignKey('product.Vehicle', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey('member.User', on_delete=models.CASCADE)
    license_code = models.CharField(max_length=20)
    battery_left = models.IntegerField(default=-1)  # -1의 경우 사용 불가.
