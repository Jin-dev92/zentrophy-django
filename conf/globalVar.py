# from enum import StrEnum

MAX_DISPLAY_LINE_COUNT = 2


class GlobalVar:
    class ErrorMessage:
        DISPLAY_LINE_DONT_EXCEEDED_SIZE = "상품 진열은 {}개를 초과할 수 없습니다.".format(MAX_DISPLAY_LINE_COUNT)
