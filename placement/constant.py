from enum import IntEnum


class PlacementType(IntEnum):
    SERVICE = 0
    DIRECT = 1
    EXCHANGE = 2


class OperationState(IntEnum):
    OPERATING = 0  # 운영중
    CONSTRUCTING = 1  # 점검중
    SOON = 2  # 설치 예정
