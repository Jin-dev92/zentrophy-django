from enum import Enum


class OrderState(Enum):
    ACCEPT_ORDER = 0
    REVIEW_DOCS = 1
    WAIT_PAYMENT = 2
    PREPARE_DELIVERY = 3
    IS_COMPLETE = 4
    IS_CANCELED = 5


class PaymentType(Enum):
    PRODUCT = 0
    VEHICLE = 1
    PERIOD = 2


