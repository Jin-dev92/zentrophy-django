from django.db import models
from sorl.thumbnail import ImageField

from placement.constant import OperationState
from util.models import SoftDeleteModel


class Placement(SoftDeleteModel):
    remote_pk = models.IntegerField(default=0)
    image = ImageField(upload_to="place/%Y/%M", null=True)
    operation_state = models.PositiveSmallIntegerField(default=OperationState.OPERATING)

    def __str__(self):
        return self.remote_pk
