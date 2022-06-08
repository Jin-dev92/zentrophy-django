# package
from django.contrib.auth import login, logout, HASH_SESSION_KEY, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ninja import NinjaAPI, Form
from ninja.security import django_auth

# util
from conf import settings
from conf.custom_exception import RefuseMustHaveReasonException, DisplayLineExceededSizeException, \
    LoginRequiredException, FormatNotSupportedException, WrongParameterException, AccessDeniedException, \
    WrongUserInfoException, WrongTokenException, NotEnoughStockException
from history.api import after_service_router as after_service_router, refund_router, warranty_router, battery_router, \
    cart_router
from member.api import router as member_router, payment_method_router
from member.models import RemoteToken
from member.schema import TokenSchema
from member.constant import RemoteTokenType
from order.api import router as order_router, subside_router, file_router
from placement.api import router as placement_router
from post.api import faq_router, notice_router, faq_category_router
from product.api import display_line_router as display_line_router
from product.api import product_router as product_router
from product.api import vehicle_router as vehicle_router
from util.exception.constant import REFUSE_MUST_HAVE_REASON, DISPLAY_LINE_DONT_EXCEEDED_SIZE, LOGIN_REQUIRED, \
    FORMAT_NOT_SUPPORTED, WRONG_PARAMETER, WRONG_TOKEN, WRONG_USER_INFO, NOT_ENOUGH_STOCK
from util.permission import is_valid_token
from util.util import ORJSONParser


# models & schema

api = NinjaAPI(parser=ORJSONParser(), csrf=not settings.DEBUG, auth=None if settings.DEBUG else django_auth)
# api = NinjaAPI(parser=ORJSONParser(), csrf=True, auth=django_auth)
API_LIST = [
    {
        'prefix': "/member/",
        'router': member_router,
        'tags': ["유저"]
    },
    {
        'prefix': "/payment_method/",
        'router': payment_method_router,
        'tags': ["결제 수단"]
    },
    {
        'prefix': "/place/",
        'router': placement_router,
        'tags': ["플레이스"]
    },
    {
        'prefix': "/product/",
        'router': product_router,
        'tags': ["상품"]
    },
    {
        'prefix': "/order/",
        'router': order_router,
        'tags': ["주문"]
    },
    {
        'prefix': "/subside/",
        'router': subside_router,
        'tags': ["보조금"]
    },
    {
        'prefix': "/upload/",
        'router': file_router,
        'tags': ["보조금 관련 파일 업로드"]
    },
    {
        'prefix': "/vehicle/",
        'router': vehicle_router,
        'tags': ["모터 사이클"]
    },
    {
        'prefix': "/display_line/",
        'router': display_line_router,
        'tags': ["상품"]
    },
    {
        'prefix': "/as/",
        'router': after_service_router,
        'tags': ["A/S"]
    },
    {
        'prefix': "/refund/",
        'router': refund_router,
        'tags': ["환불"]
    },
    {
        'prefix': "/warranty/",
        'router': warranty_router,
        'tags': ["보증 내역"]
    },
    {
        'prefix': "/battery/",
        'router': battery_router,
        'tags': ["배터리 교환 내역"]
    },
    {
        'prefix': "/faq/",
        'router': faq_router,
        'tags': ["FAQ"]
    },
    {
        'prefix': "/notice/",
        'router': notice_router,
        'tags': ["공지 사항"]
    },
    {
        'prefix': "/faq_category/",
        'router': faq_category_router,
        'tags': ["FAQ 카테고리"]
    },
    {
        'prefix': "/cart/",
        'router': cart_router,
        'tags': ["장바구니"]
    },
]

# 라우팅 설정
for item in API_LIST:
    api.add_router(prefix=item['prefix'], router=item['router'], tags=item['tags'])


@login_required
@api.get('/logout', description="로그 아웃")
def member_logout(request):
    logout(request)


# @login_required
# @api.get('/test', description="테스트용")
# def test(request):
#     print(request.session["_auth_user_hash"])
    # return


@api.post("/login", description="로그인", auth=None)
def member_login(request, token_info: TokenSchema = Form(...), email: str = Form(...), password: str = Form(...)):
    # response = HttpResponse()
    user = authenticate(request, email=email, password=password)
    print(user)
    if user is None:
        raise WrongUserInfoException

    try:
        if user.remotetoken.refresh_token and user.remotetoken.access_token:
            queryset = get_object_or_404(RemoteToken,
                              user=user,
                              access_token=is_valid_token(token_info.access_token),
                              refresh_token=is_valid_token(token_info.refresh_token),
                              )

    except Exception as e: # user가 remote token을 보유하고 있지 않을 때,
        RemoteToken.objects.create(user=user, access_token=is_valid_token(token_info.access_token), refresh_token=is_valid_token(token_info.refresh_token))

    login(request, user)
    # response['session_id'] = request.session[HASH_SESSION_KEY]
    # print(request.session[HASH_SESSION_KEY])
    # print(response)
    # return request.session[HASH_SESSION_KEY]


@api.exception_handler(exc_class=RefuseMustHaveReasonException)
def refuse_must_have_reason_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': REFUSE_MUST_HAVE_REASON['code'], 'desc': REFUSE_MUST_HAVE_REASON['desc']},
                               status=REFUSE_MUST_HAVE_REASON['status'])


@api.exception_handler(exc_class=DisplayLineExceededSizeException)
def refuse_must_have_reason_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': DISPLAY_LINE_DONT_EXCEEDED_SIZE['code'],
                                     'desc': DISPLAY_LINE_DONT_EXCEEDED_SIZE['desc']},
                               status=DISPLAY_LINE_DONT_EXCEEDED_SIZE['status']
                               )


@api.exception_handler(exc_class=LoginRequiredException)
def login_required_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': LOGIN_REQUIRED['code'],
                                     'desc': LOGIN_REQUIRED['desc'],
                                     'data': str(request.user) + "////" + "@todo 테스트 용 코드임 꼭 지울 것"
                                     },
                               status=LOGIN_REQUIRED['status']
                               )


@api.exception_handler(exc_class=FormatNotSupportedException)
def format_not_supported_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': FORMAT_NOT_SUPPORTED['code'],
                                     'desc': FORMAT_NOT_SUPPORTED['desc']},
                               status=FORMAT_NOT_SUPPORTED['status']
                               )


@api.exception_handler(exc_class=WrongParameterException)
def wrong_parameter_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': WRONG_PARAMETER['code'],
                                     'desc': WRONG_PARAMETER['desc']},
                               status=WRONG_PARAMETER['status']
                               )


@api.exception_handler(exc_class=WrongTokenException)
def wrong_token_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': WRONG_TOKEN['code'],
                                     'desc': WRONG_TOKEN['desc']},
                               status=WRONG_TOKEN['status']
                               )


@api.exception_handler(exc_class=WrongUserInfoException)
def wrong_user_info_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': WRONG_USER_INFO['code'],
                                     'desc': WRONG_USER_INFO['desc']},
                               status=WRONG_USER_INFO['status']
                               )


@api.exception_handler(exc_class=NotEnoughStockException)
def wrong_user_info_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': NOT_ENOUGH_STOCK['code'],
                                     'desc': NOT_ENOUGH_STOCK['desc']},
                               status=NOT_ENOUGH_STOCK['status']
                               )
