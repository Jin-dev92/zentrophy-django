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
