from datetime import datetime, date

from ninja import Schema, Field

from member.constant import CardCompany
from product.schema import VehicleListSchema


class MemberInsertSchema(Schema):
    username: str
    email: str
    password: str
    member_info_number: str = Field(default=None, title="유저 관련 번호", description="일반 회원이면 생년월일 8자리, 사업자면 사업자 등록번호 10자리")
    address: str
    address_detail: str
    zipcode: str
    is_business: bool = False


class MemberListSchema(Schema):
    id: int
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


class CardInsertSchema(Schema):
    card_number: str = None
    card_company: CardCompany = Field(title='카드사')
    validate_date: date = None
    security_code: str = None


class PaymentMethodListSchema(Schema):
    id: int
    card: CardInsertSchema = None
    favorite: bool = False


class PaymentMethodInsertSchema(Schema):
    name: str
    card: CardInsertSchema
