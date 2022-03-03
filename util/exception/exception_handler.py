# from conf.api import api
#
#
# class LoginRequiredException(Exception):
#     pass
# 
#
# @api.exception_handler(exc_class=LoginRequiredException)
# def login_exception_handler(request):
#     return api.create_response(request=request,
#                                data={'detail': '로그인이 필요합니다.'},
#                                status=401
#                                )