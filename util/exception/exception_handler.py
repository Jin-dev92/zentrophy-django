from django.http import HttpRequest

from conf.api import api
from util.exception.exception import LoginRequiredException
from util.exception.constant import ErrorMessage


@api.exception_handler(LoginRequiredException)
def login_required_exception_handler(request: HttpRequest):
    return api.create_response(request=request, data={'message': ErrorMessage.LOGIN_REQUIRED}, status=401)
