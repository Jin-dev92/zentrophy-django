from ninja import Schema

from order.constant import OrderState


class OrderListSchema(Schema):
    id: int
    product_name: str
    amount: int = 0
    # owner
    state: OrderState = OrderState.ACCEPT_ORDER
