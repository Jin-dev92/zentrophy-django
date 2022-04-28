# package
from ninja import NinjaAPI
from ninja.security import django_auth

# util
from conf import settings
from history.api import after_service_router as after_service_router, refund_router, warranty_router, battery_router, \
    cart_router
from member.api import router as member_router, payment_method_router
from order.api import router as order_router, subside_router, file_router
from placement.api import router as placement_router
from post.api import faq_router, notice_router, faq_category_router
from product.api import display_line_router as display_line_router
from product.api import product_router as product_router
from product.api import vehicle_router as vehicle_router
from util.util import ORJSONParser

# models & schema

api = NinjaAPI(parser=ORJSONParser(), csrf=not settings.DEBUG, auth=None if settings.DEBUG else django_auth)

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