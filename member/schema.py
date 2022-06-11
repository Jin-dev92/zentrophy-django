from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from member.constant import RemoteTokenType
from product.schema import VehicleListSchema


class TokenSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class MemberInsertSchema(Schema):
    username: str
    email: str
    password: str
    phone_number: str
    address: str
    address_detail: str
    zipcode: str
    # token_info: TokenSchema


class MemberModifySchema(Schema):
    username: str
    password: str
    address: str
    address_detail: str
    zipcode: str


class CardInsertSchema(Schema):
    card_number: str
    user_name: str
    validate_date: str
    cvc: str


class PaymentMethodListSchema(Schema):
    id: int
    name: str
    card: CardInsertSchema = None
    favorite: bool = False


class MemberOwnedVehiclesListSchema(Schema):
    id: int
    vehicle: VehicleListSchema
    license_code: str = Field(default=None, title="라이센스 코드")
    battery_left: int = Field(default=-1, title="잔여 배터리 량")


class MemberListSchema(Schema):
    id: int
    username: str
    email: str
    phone_number: str = None
    address: str
    address_detail: str
    zipcode: str
    vehicles_list: List[MemberOwnedVehiclesListSchema] = []
    payment_method: List[PaymentMethodListSchema] = []
    date_joined: datetime = None
    last_login: datetime = None


class MemberReAssignSchema(Schema):
    username: str
    email: str
    password: str


# class MemberOwnedVehiclesListSchema(Schema):
#     id: int
#     vehicle: VehicleListSchema
#     license_code: str = Field(default=None, title="라이센스 코드")
#     battery_left: int = Field(default=-1, title="잔여 배터리 량")


class PaymentMethodInsertSchema(Schema):
    name: str
    card: CardInsertSchema
