from enum import Enum


class ProductLabel(Enum):
    HOT = 0
    NEW = 1
    SALE = 2
    BEST = 3

    @classmethod  # model에서 enum사용을 위한 코드.
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


class ProductOptionsLabel(Enum):
    NORMAL = 0
    INPUT = 1
    NONE = 2

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)
