from conf.custom_exception import UserNotAccessDeniedException


def admin_permission(func):     # admin 만 접속 가능한 함수에 적용
    def decorator(request, *args, **kwargs):
        user = request.auth
        if user.is_staff and user.is_active:
            return func(request, *args, **kwargs)
        else:
            raise UserNotAccessDeniedException

    return decorator