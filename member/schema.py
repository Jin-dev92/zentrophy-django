from ninja import Schema, Field
from product.schema import VehicleListSchema


class MemberInsertSchema(Schema):
    username: str = None
    email: str = None
    address: str = None
    address_detail: str = None
    member_info_number: str = Field(
        default=None,
        description="is_business가 True 이면 사업자 등록번호, 반대면 생년원일"  # 사업자등록 번호  혹은 생년월일 vaildator가 필요함.
    )
    zipCode: str = None
    is_business: bool = False


class MemberListSchema(Schema):
    id: int
    username: str
    email: str
    address: str
    address_detail: str
    member_info_number: str = Field(
        title="유저 번호",
        description="is_business가 True 이면 사업자 등록번호, 반대면 생년원일"  # 사업자등록 번호  혹은 생년월일 vaildator가 필요함.
    )
    zipCode: str
    is_business: bool
    # is_created: datetime = None
    # is_updated: datetime = None


class AdminInsertSchema(Schema):
    username: str
    email: str
    password: str


class MemberOwnedVehiclesListSchema(Schema):
    id: int
    vehicle: VehicleListSchema
    license_code: str = Field(default=None, title="라이센스 코드")
    battery_left: int = Field(default=-1, title="잔여 배터리 량")
