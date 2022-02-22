# package
from ninja import NinjaAPI
# util
from conf import settings
from conf.contant import Env
from post.api import faq_router, notice_router, faq_category_router
from util.util import ORJSONParser
# models & schema

from member.api import router as member_router
from order.api import router as order_router
from placement.api import router as placement_router
from product.api import product_router as product_router
from product.api import vehicle_router as vehicle_router
from product.api import display_line_router as display_line_router
# from history.api import history_router as history_router
from history.api import after_service_router as after_service_router, refund_router, warranty_router, battery_router

api = NinjaAPI(parser=ORJSONParser(), csrf=(settings.Env is Env.PRODUCTION))
API_LIST = [
    {
        'prefix': "/member/",
        'router': member_router,
        'tags': ["member"]
    },
    {
        'prefix': "/place/",
        'router': placement_router,
        'tags': ["place"]
    },
    {
        'prefix': "/product/",
        'router': product_router,
        'tags': ["product"]
    },
    {
        'prefix': "/order/",
        'router': order_router,
        'tags': ["order"]
    },
    {
        'prefix': "/vehicle/",
        'router': vehicle_router,
        'tags': ["vehicle"]
    },
    {
        'prefix': "/display_line/",
        'router': display_line_router,
        'tags': ["product"]
    },
    {
        'prefix': "/as/",
        'router': after_service_router,
        'tags': ["A/S"]
    },
    {
        'prefix': "/refund/",
        'router': refund_router,
        'tags': ["Refund"]
    },
    {
        'prefix': "/warranty/",
        'router': warranty_router,
        'tags': ["Warranty"]
    },
    {
        'prefix': "/battery/",
        'router': battery_router,
        'tags': ["battery"]
    },
    {
        'prefix': "/faq/",
        'router': faq_router,
        'tags': ["faq"]
    },
    {
        'prefix': "/notice/",
        'router': notice_router,
        'tags': ["notice"]
    },
    {
        'prefix': "/faq_category/",
        'router': faq_category_router,
        'tags': ["faq_category"]
    },
    # BatteryExchange
]
# api_list.
# 라우팅 설정
for item in API_LIST:
    api.add_router(prefix=item['prefix'], router=item['router'], tags=item['tags'])
