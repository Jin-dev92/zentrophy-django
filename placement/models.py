from django.db import models
from sorl.thumbnail import ImageField

from util.models import SoftDeleteModel, FileExistModel


class Placement(SoftDeleteModel, FileExistModel):
    remote_pk = models.IntegerField(unique=True)
    image = ImageField(upload_to="place/%Y/%M", null=True)
    is_activate = models.BooleanField(default=False)

    def __str__(self):
        return int(self.remote_pk)
