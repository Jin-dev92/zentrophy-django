from datetime import datetime

from ninja import Schema, Field
from product.schema import VehicleListSchema


class MemberInsertSchema(Schema):
    username: str
    email: str
    member_info_number: str
    address: str
    address_detail: str
    zipcode: str
    is_business: bool


class MemberListSchema(Schema):
    username: str
    email: str
    member_info_number: str
    address: str
    address_detail: str
    zipcode: str
    is_business: bool
    date_joined: datetime
    last_login: datetime = None


class MemberOwnedVehiclesListSchema(Schema):
    id: int
    vehicle: VehicleListSchema
    license_code: str = Field(default=None, title="라이센스 코드")
    battery_left: int = Field(default=-1, title="잔여 배터리 량")
