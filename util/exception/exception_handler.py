from conf.custom_exception import LoginRequiredException, UserNotAccessDeniedException, MustHaveSplitWordException, \
    NotEnoughProductsException, DisplayLineExceededSizeException, ChangeOrderStateException, \
    RefuseMustHaveReasonException, AccessDeniedException, WrongBirthNumberException, WrongBusinessNumberException, \
    DataBaseORMException, FileIOException
from util.exception.constant import LOGIN_REQUIRED, USER_NOT_ACCESS_DENIED, MUST_HAVE_SPLIT_WORD, \
    CANT_SALE_STOCK_COUNT_IS_ZERO, DISPLAY_LINE_DONT_EXCEEDED_SIZE, CANT_CHANGE_ORDER_STATE, REFUSE_MUST_HAVE_REASON, \
    ACCESS_DENIED, WRONG_BIRTH_NUMBER, WRONG_BUSINESS_NUMBER, DB_ERROR, FILE_ERROR


# class ExceptionHandler:
#
#     def __init__(self):
#         pass


exception_handler_list = [
    {
        'data': {
            'massage': LOGIN_REQUIRED,
            'status_code': '1'
        },
        'exc_class': LoginRequiredException
    },
    {
        'data': {
            'massage': USER_NOT_ACCESS_DENIED,
            'status_code': '2'
        },
        'exc_class': UserNotAccessDeniedException
    },
    {
        'data': {
            'massage': MUST_HAVE_SPLIT_WORD,
            'status_code': '3'
        },
        'exc_class': MustHaveSplitWordException
    },
    {
        'data': {
            'massage': CANT_SALE_STOCK_COUNT_IS_ZERO,
            'status_code': '4'
        },
        'exc_class': NotEnoughProductsException,
    },
    {
        'data': {
            'massage': DISPLAY_LINE_DONT_EXCEEDED_SIZE,
            'status_code': '5'
        },
        'exc_class': DisplayLineExceededSizeException
    },
    {
        'data': {
            'massage': CANT_CHANGE_ORDER_STATE,
            'status_code': '6'
        },
        'exc_class': ChangeOrderStateException
    },
    {
        'data': {
            'massage': REFUSE_MUST_HAVE_REASON,
            'status_code': '7'
        },
        'exc_class': RefuseMustHaveReasonException
    },
    {
        'data': {
            'massage': ACCESS_DENIED,
            'status_code': '8'
        },
        'exc_class': AccessDeniedException
    },
    {
        'data': {
            'massage': WRONG_BIRTH_NUMBER,
            'status_code': '9'
        },
        'exc_class': WrongBirthNumberException
    },
    {
        'data': {
            'massage': WRONG_BUSINESS_NUMBER,
            'status_code': '10'
        },
        'exc_class': WrongBusinessNumberException
    },
    {
        'data': {
            'massage': DB_ERROR,
            'status_code': '11'
        },
        'exc_class': DataBaseORMException
    },
    {
        'data': {
            'massage': FILE_ERROR,
            'status_code': '12'
        },
        'exc_class': FileIOException
    },
]
