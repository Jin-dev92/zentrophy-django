from ninja import Schema, Field


class PlacementListSchema(Schema):
    id: int
    remote_pk: int = Field(description="제우스에서 가져오는 플레이스 pk, 유니크 값을 갖고 있음.")
    is_activate: bool = Field(False, description="해당 플레이스가 활성화 되어 있는지?")
    image: str = Field(None, description="플레이스 썸네일 이미지")


class PlacementInsertSchema(Schema):
    remote_pk: int = Field(description="제우스에서 가져오는 플레이스 pk, 유니크 값을 갖고 있음.")
    is_activate: bool = Field(False, description="해당 플레이스가 활성화 되어 있는지?")
