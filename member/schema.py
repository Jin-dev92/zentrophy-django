from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from conf import settings
from product.schema import VehicleListSchema


class StatisticsMember(Schema):
    member_total: int = Field(default=None, description="전체 회원 수")   # 전체 회원 수
    new_total: int = Field(default=None, description="신규 회원 수")   # 신규 회원 수
    today_total: int = Field(default=None, description="오늘 방문자 수")   # 오늘 방문자 수
    # acc_total: int = Field(default=None, description="누적 방문자 수")  # 누적 방문자 수


class TokenSchema(Schema):
    access_token: str = "f006c2f8-2d9e-44ac-9b99-0cc9dda056bc"
    refresh_token: str = "f006c2f8-2d9e-44ac-9b99-0cc9dda056bc"
    token_type: str = "Bearer"


class MemberInsertSchema(Schema):
    username: str = 'string' if settings.DEBUG else ...
    email: str = "string@string.com" if settings.DEBUG else ...
    password: str = 'string' if settings.DEBUG else ...
    phone_number: str = 'string' if settings.DEBUG else ...
    address: str = 'string' if settings.DEBUG else ...
    address_detail: str = 'string' if settings.DEBUG else ...
    zipcode: str = 'string' if settings.DEBUG else ...


class MemberModifySchema(Schema):
    username: str
    password: str
    address: str
    address_detail: str
    zipcode: str


class CardInsertSchema(Schema):
    card_number: str = '1234123412341234' if settings.DEBUG else ...
    user_name: str = 'string' if settings.DEBUG else ...
    validate_date: str = '1128' if settings.DEBUG else ...
    cvc: str = '123' if settings.DEBUG else ...
    pwd_2digit: str = '12' if settings.DEBUG else ...
    personal_number: str = '110101' if settings.DEBUG else ...
    is_business: bool = False


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
    name: str = 'string' if settings.DEBUG else ...
    card: CardInsertSchema
