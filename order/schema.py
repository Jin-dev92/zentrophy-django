from typing import List

from ninja import Schema

from order.constant import OrderState
from product.schema import ProductListSchema, VehicleListSchema
from member.schema import MemberListSchema


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    product: ProductListSchema = None
    vehicle: VehicleListSchema = None
    amount: int = 0
    state: OrderState = OrderState.ACCEPT_ORDER


class OrderCreateSchema(Schema):
    owner: int
    product: List[int] = None
    vehicle: List[int] = None
    extra_subside: List[int] = None
    amount: int = 0
