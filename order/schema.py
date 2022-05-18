from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from member.schema import MemberListSchema
from order.constant import OrderState


class CustomerInfo(Schema):
    name: str = None
    birth: date = None
    tel: str = None
    email: str = None
    is_apply_subside: bool = False


class OrderLocationInfo(Schema):
    address: str = None
    detail: str = None


class OrderedProductOptionsSchema(Schema):
    product_options_id: int = None
    amount: int = None


class OrderedVehicleColorSchema(Schema):
    vehicle_color_id: int = None
    amount: int = None


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    ordered_product_options: List[OrderedProductOptionsSchema] = None
    ordered_vehicle_color: List[OrderedVehicleColorSchema] = None
    customer_info: CustomerInfo = None
    order_location_info: OrderLocationInfo = None
    subside: int = Field(default=0, title="기본 보조금")
    extra_subside: list = Field(default=[], title="추가 보조금")
    is_visited: bool = Field(default=False, title="방문 구매 여부")
    total: int = 0
    state: OrderState = Field(default=OrderState.ACCEPT_ORDER,
                              title="주문 상태",
                              description="0: 주문 수락, 1: 서류 검토중, 2: 결제 대기중, 3: 배달 준비중, 4: 배달 완료, 5: 주문 취소")
    files: List[str] = Field(default=None, title="첨부 파일")
    is_created: datetime
    is_updated: datetime


class OrderCreateSchema(Schema):
    ordered_product_options: List[OrderedProductOptionsSchema] = None
    ordered_vehicle_color: List[OrderedVehicleColorSchema] = None
    customer_info: CustomerInfo = None
    order_location_info: OrderLocationInfo = None
    subside: bool = Field(default=False, description="기본 보조금 여부")
    extra_subside: List[int] = Field(default=None, description="추가 보조금 pk")
    total: int = 0
    is_visited: bool = Field(default=False, description="방문 구매 여부")


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
