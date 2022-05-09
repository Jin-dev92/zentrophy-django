from conf import settings
from history.constant import RefundStatus

# common error message
LOGIN_REQUIRED = {
    'code': 4010000,
    'desc': '로그인이 필요합니다.'
}
USER_NOT_ACCESS_DENIED = '일반 유저는 접근 할 수 없습니다.'
DB_ERROR = 'DB ORM Error'
FILE_ERROR = 'File I/O Error'
# member
WRONG_BUSINESS_NUMBER = '잘못된 사업자 번호 입니다.'
WRONG_BIRTH_NUMBER = '잘못된 생년월일 입니다.'
ACCESS_DENIED = '이메일 혹은 비밀번호가 틀립니다.'
# product
CANT_SALE_STOCK_COUNT_IS_ZERO = "재고량이 없어 판매할 수 없습니다."
CANT_CHANGE_ORDER_STATE = "변경 하려는 주문 상태와 db 내 주문 상태가 같습니다."
CANT_APPLY_PERIOD_PAYMENT = '정기 결제 에는 적용할 수 없습니다.'
MUST_HAVE_SPLIT_WORD = "옵션 구분 문자를 섞어 주세요. 옵션 구분 문자는 {split}입니다. ex)상품명{split}옵션명".format(split=settings.OPTION_SPLIT)
DISPLAY_LINE_DONT_EXCEEDED_SIZE = {
    'code': 4000001,
    'desc': "상품 진열은 {count}개를 초과할 수 없습니다.".format(count=settings.MAX_DISPLAY_LINE_COUNT)
}

# history
REFUSE_MUST_HAVE_REASON = {
    'code': 4000002,
    'desc': "Status가 {}인경우 반드시 거절 이유(reject_reason)가 포함 되어야 합니다.".format(RefundStatus.REFUSE)
}

DB_UNIQUE_CONSTRAINT = {
    'code': 4000003,
    'desc': "유니크 키 조건에 위배되는 값입니다."
}
