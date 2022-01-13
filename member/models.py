from django.db import models


# Create your models here.
class Member(models.Model):
    id = models.AutoField(primary_key=True, )
    user_name = models.CharField(max_length=200, null=False)
    user_mail = models.EmailField(max_length=200, unique=True, null=False)
    phone_number = models.CharField(max_length=12, null=False)
    address = models.CharField(max_length=200, null=False)
