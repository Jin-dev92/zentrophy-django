from history.constant import RefundStatus

MAX_DISPLAY_LINE_COUNT = 2
# product
DISPLAY_LINE_DONT_EXCEEDED_SIZE = "상품 진열은 {}개를 초과할 수 없습니다.".format(MAX_DISPLAY_LINE_COUNT)
# history
REFUSE_MUST_HAVE_REASON = "Status가 {}인경우 반드시 거절 이유(reject_reason)가 포함되어야합니다.".format(RefundStatus.REFUSE)
