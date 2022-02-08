from datetime import datetime
from typing import List

from ninja import Schema
from order.constant import OrderState
from member.schema import MemberListSchema


class ExtraSubsideSchema(Schema):
    id: int
    name: str
    amount: int
    description_1: str
    description_2: str


class CardInfo(Schema):
    card_no: int = None
    payment_type: int = None
    payment_method: int = None


class OrderedProductInfo(Schema):
    product_name: str = None
    amount: str = None
    price: int = 0
    total_price: int = 0


class OrderPaymentInfoSchema(Schema):  # 나이스 페이 결제 후 response 되는 데이터를 확인해야함
    card_info: CardInfo = None
    product_info: OrderedProductInfo = None


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    payment_info: OrderPaymentInfoSchema = None
    # file: str = None
    # necessary_document_file: str
    extra_subside: List[int]
    state: OrderState = OrderState.ACCEPT_ORDER
    is_created: datetime
    is_updated: datetime


class OrderCreateSchema(Schema):
    owner: int
    payment_info: OrderPaymentInfoSchema = None
    extra_subside: List[ExtraSubsideSchema] = None
