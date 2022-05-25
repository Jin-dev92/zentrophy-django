import base64

from django.http import HttpRequest

from conf.custom_exception import WrongTokenException


def has_permission(request: HttpRequest):  # 어드민 유저만 허용
    user = request.user
    return user.is_staff and user.is_active


def is_valid_token(token: str):
    if len(token) != 36:
        raise WrongTokenException
    split = token.split(sep='-', maxsplit=4)
    if len(split[0]) != 8 or len(split[1]) != 4 or len(split[2]) != 4 or len(split[3]) != 4 or len(split[4]) != 12:
        raise WrongTokenException
    return token