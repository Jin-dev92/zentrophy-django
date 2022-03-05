from enum import Enum
from conf import settings
from history.constant import RefundStatus


class ErrorMessage(Enum):
    # common error message
    LOGIN_REQUIRED = '로그인이 필요합니다.'
    # product
    CANT_SALE_STOCK_COUNT_IS_ZERO = "재고량이 없어 판매할 수 없습니다."
    CANT_CHANGE_ORDER_STATE = "변경 하려는 주문 상태와 db 내 주문 상태가 같습니다."
    CANT_APPLY_PERIOD_PAYMENT = '정기 결제 에는 적용할 수 없습니다.'
    MUST_HAVE_SPLIT_WORD = "옵션 구분 문자를 섞어 주세요. 옵션 구분 문자는 {split}입니다. ex)상품명{split}옵션명".format(
        split=settings.OPTION_SPLIT)
    DISPLAY_LINE_DONT_EXCEEDED_SIZE = "상품 진열은 {count}개를 초과할 수 없습니다.".format(count=settings.MAX_DISPLAY_LINE_COUNT)
    # history
    REFUSE_MUST_HAVE_REASON = "Status가 {}인경우 반드시 거절 이유(reject_reason)가 포함되어야합니다.".format(RefundStatus.REFUSE)
