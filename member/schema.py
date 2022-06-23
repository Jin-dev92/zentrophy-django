from datetime import datetime
from typing import List
from uuid import UUID

from ninja import Schema, Field

from conf import settings
from member.constant import MemberSort


class StatisticsMember(Schema):
    member_total: int = Field(default=None, description="전체 회원 수")   # 전체 회원 수
    new_total: int = Field(default=None, description="신규 회원 수")   # 신규 회원 수
    today_total: int = Field(default=None, description="오늘 방문자 수")   # 오늘 방문자 수
    # acc_total: int = Field(default=None, description="누적 방문자 수")  # 누적 방문자 수


class TokenSchema(Schema):
    access_token: UUID = Field(default="f006c2f8-2d9e-44ac-9b99-0cc9dda056bc", description="제우스에서 로그인 할 때 가져오는 토큰 UUID")
    refresh_token: UUID = Field(default="f006c2f8-2d9e-44ac-9b99-0cc9dda056bc", description="제우스에서 로그인 할 때 가져오는 토큰 UUID")
    token_type: str = Field(default="Bearer", description="제우스에서 가져오는 토큰 타입, 현재 BEARER만 사용하고 있으며, 나중에 추가 될 수도 있다.")


class MemberInsertSchema(Schema):
    username: str = Field(default='string' if settings.DEBUG else ..., description="유저 이름")
    email: str = Field(default="string@string.com" if settings.DEBUG else ..., description="이메일, 유저가 로그인 할때 사용하는 유니크 키(id 역할을 함)")
    password: str = Field(default='string' if settings.DEBUG else ..., description="패스워드")
    phone_number: str = Field(default='string' if settings.DEBUG else ..., description="연락처")
    address: str = Field(default='string' if settings.DEBUG else ..., description="주소")
    address_detail: str = Field('string' if settings.DEBUG else ..., description="상세 주소")
    zipcode: str = Field('string' if settings.DEBUG else ..., description="우편 번호")


class MemberModifySchema(Schema):
    username: str = Field(description="유저 이름")
    password: str = Field(description="패스 워드")
    address: str = Field(description="주소")
    address_detail: str = Field(description="상세 주소")
    zipcode: str = Field(description="우편 번호")


class CardInsertSchema(Schema):
    card_number: str = Field(default='1234123412341234' if settings.DEBUG else ..., description="카드 번호 12자리")
    user_name: str = Field(default='string' if settings.DEBUG else ..., description="카드에 명시 되어 있는 유저 이름")
    validate_date: str = Field(default='1128' if settings.DEBUG else ..., description="카드에 명시 되어 있는 유효 기간 4자리")
    cvc: str = Field(default='123' if settings.DEBUG else ..., description="cvc")
    pwd_2digit: str = Field('12' if settings.DEBUG else ..., description="카드 비밀 번호 앞 2자리")
    personal_number: str = Field('110101' if settings.DEBUG else ..., description="개인 회원 일 경우 생년월일 8자리, 사업자 회원일 경우 사업자 번호 10자리")
    is_business: bool = Field(False, description="사업자 유무, True 일 경우 사업자, False 일 경우 개인 회원")


class PaymentMethodListSchema(Schema):
    id: int
    name: str = Field(description="결제 수단 별칭")
    card: CardInsertSchema = Field(None, description="결제 수단에 사용할 카드 정보")
    favorite: bool = Field(False, description="즐겨 쓰는 결제 수단, 현재 기획 상 쓰는 곳은 없다.")


class MemberListParamsSchema(Schema):
    email: str = None
    username: str = None
    sort: MemberSort = None


class VehicleImageInOwnedVehicleSchema(Schema):
    id: int
    origin_image: str


class VehicleColorInOwnedVehicleSchema(Schema):
    color_name: str = None
    stock_count: int = None
    sale_count: int = None
    hex_code: str = None
    on_sale: bool = None
    price: int = None
    vehicle_image: List[VehicleImageInOwnedVehicleSchema] = None


class OwnedVehicleListSchema(Schema):
    vehicle_color: VehicleColorInOwnedVehicleSchema = None
    release_number: str = None


class MemberListSchema(Schema):
    id: int
    username: str = Field(description="유저 이름")
    email: str = Field(description="이메일, 유저가 로그인 할때 사용하는 유니크 키(id 역할을 함)")
    phone_number: str = Field(default=None, description="연락처")
    address: str = Field(default=None, description="주소")
    address_detail: str = Field(default=None, description="상세 주소")
    zipcode: str = Field(default=None, description="우편 번호")
    payment_method: List[PaymentMethodListSchema] = Field(default=[], description="결제 수단")
    owned_vehicle: List[OwnedVehicleListSchema] = Field(default=None, description="유저가 소유 중 인 모터 사이클 목록")
    date_joined: datetime = Field(default=None, description="가입한 시간")
    last_login: datetime = Field(default=None, description="마지막 로그인 시간")


class MemberReAssignSchema(Schema): # 비밀 번호 재생성 시 사용 되는 스키마.
    username: str = Field(description="유저 이름")
    email: str = Field(description="이메일")
    password: str = Field(description="비밀번호")


class PaymentMethodInsertSchema(Schema):
    name: str = Field('string' if settings.DEBUG else ...,  description="결제 수단 별칭, 현재 기획 상 없는 기능.")
    card: CardInsertSchema = Field(description="결제 수단 으로 사용 하는 카드 정보")
