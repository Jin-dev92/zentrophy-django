from enum import IntEnum


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