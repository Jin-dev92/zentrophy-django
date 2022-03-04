from django.http import HttpRequest


def has_permission(request: HttpRequest):  # 어드민 유저만 허용
    user = request.user
    return user.is_staff and user.is_active
