from conf.custom_exception import LoginRequiredException, UserNotAccessDeniedException, MustHaveSplitWordException, \
    NotEnoughProductsException, DisplayLineExceededSizeException
from util.exception.constant import LOGIN_REQUIRED, USER_NOT_ACCESS_DENIED, MUST_HAVE_SPLIT_WORD, \
    CANT_SALE_STOCK_COUNT_IS_ZERO, DISPLAY_LINE_DONT_EXCEEDED_SIZE

exception_handler_list = [
    {
        'data': {
            'massage': LOGIN_REQUIRED,
            'status_code': '1'
        },
        'exc_class': LoginRequiredException,
    },
    {
        'data': {
            'massage': USER_NOT_ACCESS_DENIED,
            'status_code': '2'
        },
        'exc_class': UserNotAccessDeniedException,
    },
    {
        'data': {
            'massage': MUST_HAVE_SPLIT_WORD,
            'status_code': '3'
        },
        'exc_class': MustHaveSplitWordException,
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
        'exc_class': DisplayLineExceededSizeException,
    },
]
