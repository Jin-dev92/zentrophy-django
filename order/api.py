from typing import List

from ninja import Router

from order.schema import OrderListSchema

router = Router()


@router.get("", description="주문", response={200: List[OrderListSchema]})
def get_list_order(request):
    return "aa"
