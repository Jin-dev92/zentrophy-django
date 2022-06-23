# package
import datetime

import jwt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from jwt import ExpiredSignatureError
from ninja import NinjaAPI, Form, Schema
# util
from ninja.security import HttpBearer

from conf import settings
from conf.custom_exception import RefuseMustHaveReasonException, DisplayLineExceededSizeException, \
    LoginRequiredException, FormatNotSupportedException, WrongParameterException, WrongUserInfoException, \
    WrongTokenException, NotEnoughStockException, UserNotAccessDeniedException, OrderStateCantChangeException, \
    IncorrectTotalAmountException, MustHaveDeliveryToException
from conf.settings import SECRET_KEY, JWT_ENCRYPTION_ALG
from external.api import subscription_router, payment_router, external_router
from history.api import after_service_router as after_service_router, refund_router, warranty_router, battery_router, \
    cart_router
from member.api import router as member_router, payment_method_router
from member.models import RemoteToken, User
from member.schema import TokenSchema
from order.api import router as order_router, subside_router, file_router
from placement.api import router as placement_router
from post.api import faq_router, notice_router, faq_category_router
from product.api import display_line_router as display_line_router
from product.api import product_router as product_router
from product.api import vehicle_router as vehicle_router
from util.exception.constant import REFUSE_MUST_HAVE_REASON, DISPLAY_LINE_DONT_EXCEEDED_SIZE, LOGIN_REQUIRED, \
    FORMAT_NOT_SUPPORTED, WRONG_PARAMETER, WRONG_TOKEN, WRONG_USER_INFO, NOT_ENOUGH_STOCK, USER_NOT_ACCESS_DENIED, \
    CANT_CHANGE_ORDER_STATE, INCORRECT_TOTAL_AMOUNT, MUST_HAVE_DELIVERY_TO, EXPIRED_SIGNATURE
from util.permission import is_valid_token, get_jwt_token
from util.util import ORJSONParser


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        decoded: dict = jwt.decode(token, SECRET_KEY, algorithms=JWT_ENCRYPTION_ALG)
        user = User.objects.filter(id=decoded.get('id')).first()
        return user


class LoginResponse(Schema):
    token: str


api = NinjaAPI(parser=ORJSONParser(), auth=AuthBearer(), csrf=False)

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
        'prefix': "/subscription/",
        'router': subscription_router,
        'tags': ["정기 결제"]
    },
    {
        'prefix': "/payment/",
        'router': payment_router,
        'tags': ["일반 결제"]
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
    {
        'prefix': "/external/",
        'router': external_router,
        'tags': ["외부 API"]
    },
]

# 라우팅 설정
for item in API_LIST:
    api.add_router(prefix=item['prefix'], router=item['router'], tags=item['tags']
                   , auth=AuthBearer())


@login_required
@api.get('/logout', description="로그 아웃")
def member_logout(request):
    logout(request)


@api.post("/login", description="로그인", auth=None, response=LoginResponse)
def member_login(request, token_info: TokenSchema = Form(...),
                 email: str = Form(default="admin@admin.com" if settings.DEBUG else ..., description="이메일"),
                 password: str = Form(default="Test111!" if settings.DEBUG else ..., description="패스워드")
                 ):
    user = authenticate(request, email=email, password=password)
    if user is None:
        raise WrongUserInfoException
    try:
        if len(RemoteToken.objects.filter(user=user)) == 0:
            RemoteToken.objects.create(user=user,
                                       access_token=is_valid_token(token_info.access_token),
                                       refresh_token=is_valid_token(token_info.refresh_token)
                                       )
        else:
            if user.remotetoken.refresh_token and user.remotetoken.access_token:
                target = get_object_or_404(RemoteToken, user=user)
                target.access_token = token_info.access_token
                target.refresh_token = token_info.refresh_token
                target.save(update_fields=['access_token', 'refresh_token'])

    except Exception as e:
        raise e

    login(request, user)    # 로그인
    return get_jwt_token(user.id)


@api.get('/refresh', response=LoginResponse)
def get_request_refresh_token(request):
    """
    리프레쉬 토큰 API
    """
    if not request.auth:
        raise LoginRequiredException
    return get_jwt_token(request.auth.id)

# 에러 핸들링
@api.exception_handler(exc_class=UserNotAccessDeniedException)
def user_not_access_denied_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': USER_NOT_ACCESS_DENIED['code'], 'desc': USER_NOT_ACCESS_DENIED['desc']},
                               status=USER_NOT_ACCESS_DENIED['status'])


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
                                     'data': str(request.auth) + "////" + "@todo 테스트 용 코드임 꼭 지울 것"
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
def not_enough_stock_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': NOT_ENOUGH_STOCK['code'],
                                     'desc': NOT_ENOUGH_STOCK['desc']},
                               status=NOT_ENOUGH_STOCK['status']
                               )


@api.exception_handler(exc_class=OrderStateCantChangeException)
def cant_change_order_state_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': CANT_CHANGE_ORDER_STATE['code'],
                                     'desc': CANT_CHANGE_ORDER_STATE['desc']},
                               status=CANT_CHANGE_ORDER_STATE['status']
                               )


@api.exception_handler(exc_class=IncorrectTotalAmountException)
def incorrect_total_amount_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': INCORRECT_TOTAL_AMOUNT['code'],
                                     'desc': INCORRECT_TOTAL_AMOUNT['desc']},
                               status=INCORRECT_TOTAL_AMOUNT['status']
                               )


@api.exception_handler(exc_class=MustHaveDeliveryToException)
def must_have_delivery_to_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': MUST_HAVE_DELIVERY_TO['code'],
                                     'desc': MUST_HAVE_DELIVERY_TO['desc']},
                               status=MUST_HAVE_DELIVERY_TO['status']
                               )


@api.exception_handler(exc_class=ExpiredSignatureError)
def expired_signature_exception_handler(request, exec):
    return api.create_response(request,
                               data={'code': EXPIRED_SIGNATURE['code'],
                                     'desc': EXPIRED_SIGNATURE['desc']},
                               status=EXPIRED_SIGNATURE['status']
                               )
