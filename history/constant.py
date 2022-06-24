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


class DrivingStyle(IntEnum):
    HARD = 0
    NORMAL = 1
    SAFE = 2


class InternalCombustionEngineType(IntEnum):
    ENGINE_OIL = 0
    AIR_CLEANER = 1
    IGNITION_PLUG = 2
    FRONT_TIRE = 3
    MISSION_OIL = 4
    BACK_TIRE = 5
    BREAK_PAD = 6
    ACTUATOR = 7


class ExpendablesType(IntEnum):
    GEAR_OIL = 0,
    FRONT_TIRE = 1,
    BREAK_PAD = 2,
    BACK_TIRE = 3,
    ACTUATOR = 4