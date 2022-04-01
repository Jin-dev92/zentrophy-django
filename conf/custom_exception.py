class LoginRequiredException(Exception):
    pass


class UserNotAccessDeniedException(Exception):
    pass


class MustHaveSplitWordException(Exception):
    pass


class NotEnoughProductsException(Exception):
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


class WrongBirthNumberException(Exception):
    pass


class WrongBusinessNumberException(Exception):
    pass


class WrongAmountVehicleColorException(Exception):
    pass


class MemberAlreadyExistsException(Exception):
    pass
