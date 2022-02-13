from ninja import Schema

from member.schema import MemberOwnedVehiclesListSchema
from placement.schema import PlacementListSchema


class HistoryListSchema(Schema):
    id: int = None


class AfterServiceInsertSchema(Schema):
    place_id: int
    member_id: int


class AfterServiceListSchema(Schema):
    # place = models.ForeignKey('placement.Placement', on_delete=models.CASCADE)
    # vehicle = models.ForeignKey('member.MemberOwnedVehicles', on_delete=models.CASCADE, null=True)
    # registration_number = models.CharField(max_length=LICENSE_NUMBER_LENGTH, unique=True)
    # status = models.PositiveSmallIntegerField(default=AfterServiceStatus.APPLY_WAITING)
    place: PlacementListSchema = None
    # vehicle_list: MemberOwnedVehiclesListSchema = None
