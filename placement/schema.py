from enum import IntEnum

from ninja import Schema

from placement.constant import PlacementType, OperationState


class PlacementListSchema(Schema):
    id: int
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType
    operation_start: str
    operation_end: str
    operation_state: OperationState


class PlacementInsertSchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType
    operation_start: str
    operation_end: str
    operation_state: OperationState


class PlacementModifySchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType
    operation_start: str
    operation_end: str
    operation_state: OperationState
