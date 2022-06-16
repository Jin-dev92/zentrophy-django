from conf import settings
from history.constant import RefundStatus

# common error message
LOGIN_REQUIRED = {
    'code': 4010000,
    'desc': '로그인이 필요합니다.',
    'status': 401
}
DB_ERROR = 'DB ORM Error'
FILE_ERROR = 'File I/O Error'
# member
WRONG_BUSINESS_NUMBER = '잘못된 사업자 번호 입니다.'
WRONG_BIRTH_NUMBER = '잘못된 생년월일 입니다.'
ACCESS_DENIED = '이메일 혹은 비밀번호가 틀립니다.'
# product
CANT_APPLY_PERIOD_PAYMENT = '정기 결제 에는 적용할 수 없습니다.'
MUST_HAVE_SPLIT_WORD = "옵션 구분 문자를 섞어 주세요. 옵션 구분 문자는 {split}입니다. ex)상품명{split}옵션명".format(split=settings.OPTION_SPLIT)
DISPLAY_LINE_DONT_EXCEEDED_SIZE = {
    'code': 4000001,
    'desc': "상품 진열은 {count}개를 초과할 수 없습니다.".format(count=settings.MAX_DISPLAY_LINE_COUNT)
}

# history
REFUSE_MUST_HAVE_REASON = {
    'code': 4000002,
    'desc': "Status가 {}인경우 반드시 거절 이유(reject_reason)가 포함 되어야 합니다.".format(RefundStatus.REFUSE),
    'status': 400
}

DB_UNIQUE_CONSTRAINT = {
    'code': 4000003,
    'desc': "유니크 키 조건에 위배 되는 값 입니다.",
    'status': 400

}
FORMAT_NOT_SUPPORTED = {
    'code': 4000005,
    'desc': "지원 하지 않는 값 입니다. 데이터를 확인하세요",
    'status': 400
}

WRONG_PARAMETER = {
    'code': 4000006,
    'desc': "잘못된 파라미터 입니다. 데이터를 확인하세요",
    'status': 400
}
NOT_ENOUGH_STOCK = {
    'code': 4000007,
    'desc': "재고량이 부족합니다.",
    'status': 400
}

CANT_CHANGE_ORDER_STATE = {
    'code': 4000008,
    'desc': "주문 취소 상태의 주문은 상태를 다시 바꿀 수 없습니다.",
    'status': 400
}

INCORRECT_TOTAL_AMOUNT = {
    'code': 4000009,
    'desc': "요청한 금액과 실제 계산된 금액이 맞지 않습니다.",
    'status': 400
}

MUST_HAVE_DELIVERY_TO = {
    'code': 4000010,
    'desc': "탁송 배송은 반드시 배송지 주소를 포함 하여야 합니다.",
    'status': 400
}

WRONG_TOKEN = {
    'code': 4010001,
    'desc': "잘못된 토큰 입니다. 데이터를 확인하세요",
    'status': 401
}
WRONG_USER_INFO = {
    'code': 4010002,
    'desc': "아이디 혹은 비밀번호가 틀립니다.",
    'status': 401
}

USER_NOT_ACCESS_DENIED = {
    'code': 4010003,
    'desc': "일반 유저는 접근 할 수 없습니다.",
    'status': 401
}

EXPIRED_SIGNATURE = {
    'code': 4010004,
    'desc': "만료된 토큰 입니다. 다시 로그인 해주세요.",
    'status': 401
}