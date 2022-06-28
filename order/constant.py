from enum import IntEnum


class OrderState(IntEnum):
    ACCEPT_ORDER = 0
    REVIEW_DOCS = 1
    WAIT_PAYMENT = 2
    PREPARE_DELIVERY = 3
    IS_COMPLETE = 4
    IS_CANCELED = 5


class DeliveryCompany(IntEnum):
    CJ = 0
    HANJIN = 1


class DeliveryMethod(IntEnum):
    DEPEND_ON = 0
    YOURSELF = 1
