from ninja import Schema


class PlacementListSchema(Schema):
    id: int
    remote_pk: int
    is_activate: bool = False
    image: str = None


class PlacementInsertSchema(Schema):
    remote_pk: int
    is_activate: bool = False


class PlacementModifySchema(Schema):
    remote_pk: int
    is_activate: bool = False
