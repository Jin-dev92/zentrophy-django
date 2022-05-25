import base64

from django.http import HttpRequest


def has_permission(request: HttpRequest):  # 어드민 유저만 허용
    user = request.user
    return user.is_staff and user.is_active


def get_access_token(email: str, password: str):
    token = base64.b64encode(bytes(email + password, 'utf-8'))
    return token
