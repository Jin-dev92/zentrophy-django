from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from product.schema import VehicleListSchema


class StatisticsMember(Schema):
    member_total: int = Field(default=None, description="전체 회원 수")   # 전체 회원 수
    new_total: int = Field(default=None, description="신규 회원 수")   # 신규 회원 수
    today_total: int = Field(default=None, description="오늘 방문자 수")   # 오늘 방문자 수
    # acc_total: int = Field(default=None, description="누적 방문자 수")  # 누적 방문자 수


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
    pwd_2digit: str
    personal_number: str
    is_business: bool


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
    # vehicles_list: List[MemberOwnedVehiclesListSchema] = []
    payment_method: List[PaymentMethodListSchema] = []
    date_joined: datetime = None
    last_login: datetime = None


class MemberReAssignSchema(Schema):
    username: str
    email: str
    password: str


class PaymentMethodInsertSchema(Schema):
    name: str
    card: CardInsertSchema
