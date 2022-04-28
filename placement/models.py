from django.db import models
from sorl.thumbnail import ImageField

from placement.constant import PlacementType, OperationState
from util.models import TimeStampModel, SoftDeleteModel


class Placement(SoftDeleteModel):
    remote_pk = models.IntegerField(default=0)
    image = ImageField(upload_to="place/%Y/%M", null=True)
    operation_state = models.PositiveSmallIntegerField(default=OperationState.OPERATING)

    # id = models.AutoField(primary_key=True)
    # placement_name = models.CharField(max_length=100, blank=True, null=False)
    # placement_owner = models.CharField(max_length=20, blank=True, null=False)
    # placement_address = models.CharField(max_length=100, blank=True, null=False)
    # placement_type = models.PositiveSmallIntegerField(default=PlacementType.SERVICE)
    # operation_start = models.TimeField(null=False)
    # operation_end = models.TimeField(null=False)

    def __str__(self):
        return self.remote_pk
