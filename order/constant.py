from enum import Enum


class OrderState(Enum):
    ACCEPT_ORDER = 0
    REVIEW_DOCS = 1
    WAIT_PAYMENT = 2
    PREPARE_DELIVERY = 3
    IS_COMPLETE = 4
    IS_CANCELED = 5


class ErrorMessage(Enum):
    CANT_SALE_STOCK_COUNT_IS_ZERO = "재고량이 없어 판매할 수 없습니다."
    CANT_CHANGE_ORDER_STATE = "변경하려는 주문 상태와 db 내 주문 상태가 같습니다."
