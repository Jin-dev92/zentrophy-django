from ninja import Schema


class PlacementListSchema(Schema):
    id: int
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: int
    operation_start: str
    operation_end: str
    operation_state: int


class PlacementInsertSchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: int
    operation_start: str
    operation_end: str
    operation_state: int


class PlacementModifySchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: int
    operation_start: str
    operation_end: str
    operation_state: int
