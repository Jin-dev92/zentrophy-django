from django.db import models


# Create your models here.
class Member(models.Model):
    user_name = models.CharField(max_length=200)
    user_mail = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=12)
    address = models.CharField(max_length=200)