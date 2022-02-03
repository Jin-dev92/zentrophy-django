from typing import List

from ninja import Router
from django.shortcuts import get_list_or_404, get_object_or_404
from order.models import Order
from order.schema import OrderListSchema

router = Router()


@router.get("", description="전체 주문 조회", response={200: List[OrderListSchema]})
def get_list_order(request):
    return Order.objects.all()


@router.get("", description="id로 특정 주문 조회", response={200: OrderListSchema})
def get_list_order_by_id(request, id: int):
    return get_object_or_404(Order, id=id).delete()
