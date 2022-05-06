from enum import IntEnum


class ProductLabel(IntEnum):
    HOT = 0
    NEW = 1
    SALE = 2
    BEST = 3


class ProductOptionsLabel(IntEnum):
    NORMAL = 0
    INPUT = 1
    NONE = 2


class ProductListSort(IntEnum):
    # RECENT = 0
    # LATEST = 1
    # HIGH_SALE = 2
    # LOW_SALE = 3
    # HIGH_STOCK_COUNT = 4
    # LOW_STOCK_COUNT = 5
    # HIGH_DISPLAY_LINE = 6
    # LOW_DISPLAY_LINE = 7
    CREATED_AT = 0
    SALE_COUNT = 1
    STOCK_COUNT = 2
    # DISPLAY_LINE = 3
    # 최신 등록순
    # 나중 등록순
    # 낮은, 높은 판매량 순
    # 진열 라인 (진열 관리 탭에 등록 되어있는 모든 옵션들)
    # 재고 상태, 재고 보유,재고 소진
