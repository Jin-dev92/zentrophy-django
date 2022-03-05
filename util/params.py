from typing import List, Optional

from django.core.handlers.wsgi import WSGIRequest


def able2_parse_type(obj, want2type: type):
    try:
        want2type(obj)
        return True
    except Exception:
        return False


def prepare_for_query(request: WSGIRequest, exceptions: Optional[List] = None):  # exceptions : 제외 대상
    if len(request.GET) == 0:
        return dict()
    params = request.GET.copy().dict()
    if exceptions is not None:
        for exception in exceptions:
            del params[exception]
    result = {k: int(v) for k, v in params.items() if able2_parse_type(v, int)}
    not_int_value_dict = {k: v for k, v in params.items() if not able2_parse_type(v, int)}
    result.update(not_int_value_dict)
    return result
