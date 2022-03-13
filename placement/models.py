from django.db import models

from placement.constant import PlacementType, OperationState
from util.models import TimeStampModel
from sorl.thumbnail import ImageField


class Placement(models.Model):
    id = models.AutoField(primary_key=True)
    placement_name = models.CharField(max_length=100, blank=True, null=False)
    placement_owner = models.CharField(max_length=20, blank=True, null=False)
    placement_address = models.CharField(max_length=100, blank=True, null=False)
    placement_type = models.PositiveSmallIntegerField(choices=PlacementType.choices, default=PlacementType.SERVICE)
    operation_start = models.TimeField(null=False)
    operation_end = models.TimeField(null=False)
    operation_state = models.PositiveSmallIntegerField(choices=OperationState.choices, default=OperationState.OPERATING)

    def __str__(self):
        return self.placement_name


class PlacementImage(TimeStampModel):
    id = models.AutoField(primary_key=True)
    place = models.ForeignKey(Placement, on_delete=models.CASCADE)
    file = ImageField(upload_to="place/%Y/%M", null=True)
