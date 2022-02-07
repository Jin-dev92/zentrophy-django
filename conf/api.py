# package
from ninja import NinjaAPI
# from ninja.security import
# from ninja.responses import codes_4xx
# util
from util.util import ORJSONParser
# models & schema

from member.api import router as member_router
from order.api import router as order_router
from placement.api import router as placement_router
from product.api import router as product_router
from post.api import router as post_router

api = NinjaAPI(parser=ORJSONParser())

API_LIST = [
    {
        'prefix': "/member",
        'router': member_router,
        'tags': ["member"]
    },
    {
        'prefix': "/place",
        'router': placement_router,
        'tags': ["place"]
    },
    {
        'prefix': "/product",
        'router': product_router,
        'tags': ["product"]
    },
    {
        'prefix': "/post",
        'router': post_router,
        'tags': ["post"]
    },
    {
        'prefix': "/order",
        'router': order_router,
        'tags': ["order"]
    },
]





# api_list.
# 라우팅 설정
for item in API_LIST:
    api.add_router(prefix=item['prefix'], router=item['router'], tags=item['tags'])
