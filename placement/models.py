from django.db import models
from sorl.thumbnail import ImageField

from util.models import SoftDeleteModel


class Placement(SoftDeleteModel):
    remote_pk = models.IntegerField(default=0)
    image = ImageField(upload_to="place/%Y/%M", null=True)
    is_activate = models.BooleanField(default=False)

    def __str__(self):
        return self.remote_pk
