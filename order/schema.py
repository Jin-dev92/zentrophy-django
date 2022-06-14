from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from member.schema import MemberListSchema
from order.constant import OrderState
from product.schema import VehicleColorListSchema, ProductOptionsListSchema, ProductImageListSchema


class CustomerInfoSchema(Schema):
    name: str = None
    birth: date = None
    tel: str = None
    email: str = None
    is_business: bool = False
    is_apply_subside: bool = False


class OrderLocationInfoSchema(Schema):
    address_1: str = None
    address_2: str = None
    address_3: str = None
    detail: str = None


class OrderedProductOptionsListSchema(Schema):
    product_options: ProductOptionsListSchema = None
    product_image: str = None
    amount: int = None


class OrderedVehicleColorListSchema(Schema):
    # vehicle_color_id: int = None
    vehicle_color: VehicleColorListSchema = None
    amount: int = None


class OrderedProductOptionsCreateSchema(Schema):
    product_options_id: int = None
    amount: int = None


class OrderedVehicleColorCreateSchema(Schema):
    vehicle_color_id: int = None
    amount: int = None


class DocumentFileListSchema(Schema):
    id: int
    file: str = None


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    ordered_product_options: List[OrderedProductOptionsListSchema] = None
    ordered_vehicle_color: List[OrderedVehicleColorListSchema] = None
    customer_info: CustomerInfoSchema = None
    order_location_info: OrderLocationInfoSchema = None
    subside: int = Field(default=0, title="기본 보조금")
    is_visited: bool = Field(default=False, title="방문 구매 여부")
    total: int = 0
    state: OrderState = Field(default=OrderState.ACCEPT_ORDER,
                              title="주문 상태",
                              description="0: 주문 수락, 1: 서류 검토중, 2: 결제 대기중, 3: 배달 준비중, 4: 배달 완료, 5: 주문 취소")
    files: List[DocumentFileListSchema] = Field(default=None, title="첨부 파일")
    is_created: datetime
    is_updated: datetime


class OrderCreateSchema(Schema):
    ordered_product_options: List[OrderedProductOptionsCreateSchema] = Field(default=None, description="주문할 상품 옵션 > 해당 사항 없으면 보내지 마세요")
    ordered_vehicle_color: List[OrderedVehicleColorCreateSchema] = Field(default=None, description="주문할 모터 사이클 색깔 > 해당 사항 없으면 보내지 마세요")
    customer_info: CustomerInfoSchema = None
    order_location_info: OrderLocationInfoSchema = None
    subside: bool = Field(default=False, description="기본 보조금 여부")
    extra_subside: List[int] = Field(default=None, description="추가 보조금 pk")
    total: int = 0
    is_visited: bool = Field(default=False, description="방문 구매 여부")


# class OrderModifySchema(Schema):
#     customer_info: CustomerInfoSchema = None
#     order_location_info: OrderLocationInfoSchema = None
#

class ExtraSubsideListSchema(Schema):
    id: int
    name: str
    amount: int = 0
    description_1: str = ""
    description_2: str = ""


class ExtraSubsideInsertSchema(Schema):
    name: str
    amount: int = 0
    description_1: str = ""
    description_2: str = ""


class SubsideListSchema(Schema):
    id: int
    amount: int = 0
    extra: List[ExtraSubsideListSchema] = None


class SubsideInsertSchema(Schema):
    amount: int = 0
    extra: List[ExtraSubsideInsertSchema] = None


class DocumentFormatListSchema(Schema):
    id: int
    file: str = None


class Subscriptions(Schema):
    card_number: str
    expiry: str = Field(description="카드 유효기간")
    birth: str
    pwd_2digit: str = Field(description="카드 비밀번호 앞 두자리")


class SubscriptionsCreateSchema(Subscriptions):
    customer_uid: str


class RequestPaymentSubscriptionsSchema(Schema):
    customer_uid: str
    merchant_uid: str
    amount: int
    name: str


class Schedule(Schema):
    merchant_uid: str
    schedule_at: int = Field(description="결제 시도 시각, 타임스탬프로 보내기")
    amount: int
    name: str
    buyer_name: str
    buyer_tel: str
    buyer_email: str


class RequestPaymentSubscriptionsScheduleSchema(Schema):
    customer_uid: str
    schedules: List[Schedule]