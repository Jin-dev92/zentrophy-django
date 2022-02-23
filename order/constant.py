from enum import Enum

from conf import settings


class OrderState(Enum):
    ACCEPT_ORDER = 0
    REVIEW_DOCS = 1
    WAIT_PAYMENT = 2
    PREPARE_DELIVERY = 3
    IS_COMPLETE = 4
    IS_CANCELED = 5


class PaymentType(Enum):
    PRODUCT = 0
    VEHICLE = 1
    PERIOD = 2


class ErrorMessage(Enum):
    CANT_SALE_STOCK_COUNT_IS_ZERO = "재고량이 없어 판매할 수 없습니다."
    CANT_CHANGE_ORDER_STATE = "변경하려는 주문 상태와 db 내 주문 상태가 같습니다."
    CANT_APPLY_PERIOD_PAYMENT = '정기 결제 에는 적용할 수 없습니다.'
    MUST_HAVE_SPLIT_WORD = "옵션 구분 문자를 섞어 주세요. 옵션 구분 문자는 {split}입니다. ex)상품명{split}옵션명".format(
        split=settings.OPTION_SPLIT)
