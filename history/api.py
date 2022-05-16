from datetime import date
from typing import List

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ninja import Router

from conf.custom_exception import RefuseMustHaveReasonException, LoginRequiredException
from history.constant import AfterServiceStatus, RefundMethod, RefundStatus
from history.models import AfterService, Refund, Warranty, Cart
from history.schema import AfterServiceInsertSchema, RefundInsertSchema, WarrantyInsertSchema, CartListSchema, \
    CartCreateSchema, AfterServiceListSchema, RefundListSchema, \
    WarrantyListSchema
from member.models import MemberOwnedVehicles
from order.models import Order
from placement.models import Placement
from product.models import Product
from util.params import prepare_for_query

refund_router = Router()
after_service_router = Router()
warranty_router = Router()
battery_router = Router()
cart_router = Router()


# A/S
@login_required
@after_service_router.get("/", description="a/s 특정한 내역", response=List[AfterServiceListSchema])
def get_after_service_list(request, status: AfterServiceStatus = None, is_created__gte: date = None,
                           is_created__lte: date = None):
    params = prepare_for_query(request=request)
    queryset = AfterService.objects.get_queryset(**params).select_related('place', 'owned_vehicle', 'user')
    return queryset


@login_required
@after_service_router.get('/{id}', description="a/s get by id",
                          auth=None,
                          response=AfterServiceListSchema)
def get_after_service_by_id(request, id: int):
    queryset = AfterService.objects.get_queryset(id=id, user=request.user).select_related('place', 'vehicle', 'user')
    return queryset


@login_required
@after_service_router.post("/", description="a/s 내역 생성 / 수정")
def create_after_service_history(request, payload: AfterServiceInsertSchema):
    if not request.user.is_authenticated:
        raise LoginRequiredException
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k in {'place_id', 'owned_vehicle_id'}}
    place = Placement.objects.get_queryset(id=params.get('place_id'))
    owned_vehicle = MemberOwnedVehicles.objects.get_queryset(owner=request.user, id=params['owned_vehicle_id'])
    AfterService.objects.update_or_create(user=request.user, place=place.first(), owned_vehicle=owned_vehicle.first(),
                                          defaults=except_params)


# @login_required
# @after_service_router.put("/", description="a/s 상태 수정")
# def modify_after_service(request, id: int, payload: AfterServiceInsertSchema):
#     obj = get_object_or_404(AfterService, id=id, user=request.user)
#     queryset = obj.objects.update(**payload.dict())
#     obj.save()
#     return queryset


@after_service_router.delete("/", description="a/s 상태 삭제")
def delete_after_service(request, id: int):
    obj = get_object_or_404(AfterService, id=id, user=request.user)
    obj.soft_delete()


@login_required
@refund_router.get("/", description="환불 내역 조회",
                   response=List[RefundListSchema],
                   # response=ResponseDefaultHeader.Schema,
                   # auth=None
                   )
def get_refund_list(request, method: RefundMethod = None, status: RefundStatus = None):
    params = prepare_for_query(request=request)
    qs = Refund.objects.get_queryset(**params).select_related('order').all()
    return qs


@login_required
@refund_router.get("/{id}", description="환불 내역 pk로 조회")
def get_refund_by_id(id: int):
    queryset = Refund.objects.get_queryset(id=id)
    return queryset


@login_required
@refund_router.post("/", description="환불 내역 생성")
def create_refund_history(request, payload: RefundInsertSchema):
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k in {'order_id'}}
    order = get_object_or_404(Order, id=params.get('order_id'), deleted_at__isnull=True)
    queryset = Refund.objects.create(order=order, **except_params)
    return queryset


@login_required
@refund_router.put("/", description="환불 상태 변경, status 가 3일 경우 reject_reason 필수")
def modify_refund(request, id: int, status: RefundStatus, reject_reason: str = None):
    if status == RefundStatus.REFUSE and reject_reason is None:
        raise RefuseMustHaveReasonException
    target = get_object_or_404(Refund, id=id, deleted_at__isnull=True)
    target.reject_reason = reject_reason
    target.status = status
    target.save(update_fields=['reject_reason', 'status'])


@login_required
@refund_router.delete('/', description="환불 내역 삭제")
def delete_refund(request, id: int):
    target = get_object_or_404(Refund, id=id)
    target.soft_delete()


@warranty_router.get('/', description="보증 범위 리스트",
                     response=List[WarrantyListSchema]
                     )
def get_warranty_list(request, is_warranty: bool = True):
    # params = prepare_for_query(request)
    qs = Warranty.objects.get_queryset(is_warranty=is_warranty)
    return qs


@warranty_router.post('/', description="보증 범위 객체 생성 / 수정")
def create_or_update_warranty(request, payload: WarrantyInsertSchema, id: int = None):
    Warranty.objects.update_or_create(id=id, defaults=payload.dict())


@warranty_router.delete('/', description="보증 범위 객체 삭제")
def delete_warranty(request, id: int):
    qs = get_object_or_404(Warranty, id=id).soft_delete()
    return qs


@login_required
@cart_router.get('/', description="장바구니 목록 확인", response={200: List[CartListSchema]})
def get_cart_list(request):
    queryset = Cart.objects.get_queryset(owner=request.user, deleted_at__isnull=True).select_related(
        'product_options')
    return queryset


@login_required
@cart_router.post('/', description="장바구니 목록 생성")
def create_cart(request, payload: CartCreateSchema):
    product_options_id = payload.dict()['product_options_id']
    amount = payload.dict()['amount']
    queryset = Cart.objects.create(
        product_options=get_object_or_404(Product, id=product_options_id),
        owner=request.user,
        amount=amount
    )
    return queryset


@login_required
@cart_router.delete('/', description="장바구니 삭제")
def delete_cart(request, id: int):
    queryset = get_object_or_404(Cart, id=id).delete()
    return queryset
