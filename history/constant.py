from enum import IntEnum


class RefundMethod(IntEnum):
    RECALL_REQUEST = 0
    DIRECT = 1


class RefundStatus(IntEnum):
    WAITING = 0
    COMPLETED = 1
    ACCEPTED = 2
    REFUSE = 3


class AfterServiceStatus(IntEnum):
    APPLY_WAITING = 0
    APPLY_COMPLETED = 1
    ON_PROGRESS = 2
    PROGRESS_COMPLETED = 3


class AfterServiceCategory(IntEnum):
    REG_CHECK = 0  # 정기점검
    TIRE_CHECK = 1
    BREAK_PAD_CHECK = 2
    CHAIN_CHECK = 3
    CONSUME = 4  # 소모품
    ETC = 5


# [정렬] -  { 최근 지불 일정, 늦은 지불 일정, 높은 요금 순, 낮은 요금 순 , 누적 사용량 높은 순 , 누적 사용량 낮은 순 }
class BatteryExchangeSort(IntEnum):
    RECENT_PAYMENT_DATE = 0
    LATEST_PAYMENT_DATE = 1
    HIGH_PAYMENT = 2
    LOW_PAYMENT = 3
    HIGH_USED_BATTERY = 4
    LOW_USED_BATTERY = 5
