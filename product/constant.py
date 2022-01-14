from enum import Enum


class ProductLabel(Enum):
    HOT = 0,
    NEW = 1,
    SALE = 2,
    BEST = 3


class ProductOptionsLabel(Enum):
    NORMAL = 0,
    INPUT = 1,
    NONE = 2
