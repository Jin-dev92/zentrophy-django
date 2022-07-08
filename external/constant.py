from enum import Enum

from util.util import StrEnum


class Prodcd(StrEnum):
    ADVANCED = "B034"   # 고급 휘발유
    NORMAL = "B027" # 일반 휘발유
    DIESEL = "D047" # 경우
    KEROSENE = "C004"   # 실내 등유
    BUTAN = "K015"  #   자동차 부탄


class MerchantUIDType(Enum):
    PRODUCT = 0
    SUBSCRIPTION = 1