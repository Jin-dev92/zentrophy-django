class LoginRequiredException(Exception):
    pass


class UserNotAccessDeniedException(Exception):
    pass


class NotEnoughStockException(Exception):
    pass


class DisplayLineExceededSizeException(Exception):
    pass


class ChangeOrderStateException(Exception):
    pass


class RefuseMustHaveReasonException(Exception):
    pass


class DataBaseORMException(Exception):
    pass


class FileIOException(Exception):
    pass


class AccessDeniedException(Exception):
    pass


class WrongAmountVehicleColorException(Exception):
    pass


class AlreadyExistsException(Exception):
    pass


class IncorrectTotalAmountException(Exception):
    pass


class WrongParameterException(Exception):
    pass


class WrongUserInfoException(Exception):
    pass


class WrongTokenException(Exception):
    pass


class FormatNotSupportedException(Exception):
    pass


class AdminAccountInActiveException(Exception):
    pass


class OrderStateCantChangeException(Exception):
    pass


class MustHaveDeliveryToException(Exception):
    pass


class IncorrectOrderStateException(Exception):
    pass


class PrevEstimateHaveOneException(Exception):
    pass


class ForgedOrderException(Exception):
    pass