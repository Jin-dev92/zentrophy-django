from datetime import datetime
from typing import List

from ninja import Schema, Field

from member.schema import MemberListSchema, PaymentMethodListSchema
from order.constant import OrderState, PaymentType


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    payment_method: PaymentMethodListSchema = Field(title="결제 수단")
    is_able_subside: bool = Field(title="기본 보조금 가능 여부")
    extra_subside: List[int] = Field(title="추가 보조금 pk list")
    state: OrderState = Field(default=OrderState.ACCEPT_ORDER,
                              title="주문 상태",
                              description="0: 주문 수락, 1: 서류 검토중, 2: 결제 대기중, 3: 배달 준비중, 4: 배달 완료, 5: 주문 취소")
    is_created: datetime
    is_updated: datetime
    files: str = Field(default=None, title="첨부 파일")


class OrderDetailSchema(Schema):
    product_options: int = None
    vehicle_color: int = None
    amount: int = 0


class OrderCreateSchema(Schema):
    payment_type: PaymentType
    payment_info: dict = Field(default=None,
                               title="결제 정보",
                               description="결제 후 return 되는 결제 관련 값을 넣어줘야함")
    order_detail: List[OrderDetailSchema] = None
    payment_method: int = Field(title="결제 수단 pk")
    is_able_subside: bool = False
    extra_subside_id: List[int] = Field(default=None, description="추가 보조금 pk")


class SubsideListSchema(Schema):
    name: str
    amount: int
    is_based: bool = False
    description_1: str = ""
    description_2: str = ""


class SubsideInsertSchema(Schema):
    name: str
    amount: int
    is_based: bool
    description_1: str = ""
    description_2: str = ""
