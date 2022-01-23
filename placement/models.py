from django.db import models

from placement.constant import PlacementType, OperationState


class Placement(models.Model):
    id = models.AutoField(primary_key=True)
    placement_name = models.CharField(max_length=100, blank=True, null=False)
    placement_owner = models.CharField(max_length=20, blank=True, null=False)
    placement_address = models.CharField(max_length=100, blank=True, null=False)
    placement_type = models.PositiveSmallIntegerField(default=PlacementType.SERVICE)
    operation_start = models.CharField(max_length=10, blank=True, null=False)
    operation_end = models.CharField(max_length=10, blank=True, null=False)
    operation_state = models.PositiveSmallIntegerField(default=OperationState.OPERATING)
