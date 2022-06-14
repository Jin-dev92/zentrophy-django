from datetime import date
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from django.db.models import F

from conf.custom_exception import RefuseMustHaveReasonException, LoginRequiredException, UserNotAccessDeniedException
from history.constant import AfterServiceStatus, RefundMethod, RefundStatus
from history.models import AfterService, Refund, Warranty, Cart
from history.schema import AfterServiceInsertSchema, RefundInsertSchema, WarrantyInsertSchema, CartListSchema, \
    CartCreateSchema, AfterServiceListSchema, RefundListSchema, \
    WarrantyListSchema
from order.models import Order
from placement.models import Placement
from product.models import ProductOptions
from util.decorator import admin_permission
from util.number import generate_random_number
from util.params import prepare_for_query
from util.permission import is_admin

refund_router = Router()
after_service_router = Router()
warranty_router = Router()
battery_router = Router()
cart_router = Router()


@after_service_router.get("/", description="a/s 특정한 내역", response=List[AfterServiceListSchema])
def get_after_service_list(request, status: AfterServiceStatus = None, is_created__gte: date = None,
                           is_created__lte: date = None):
    params = prepare_for_query(request=request)
    if request.auth.is_staff and request.auth.is_active:
        target = AfterService.objects.get_queryset(**params)
    else:
        target = AfterService.objects.get_queryset(**params, user=request.auth)
    queryset = target.select_related('place', 'user')
    return queryset


@after_service_router.post("/", description="a/s 내역 생성 / 수정")
def update_or_create_after_service_history(request, payload: AfterServiceInsertSchema):
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k in {'place_id'}}
    except_params['registration_number'] = generate_random_number()
    place = Placement.objects.get_queryset(id=params.get('place_id'))
    AfterService.objects.update_or_create(user=request.auth, place=place.first(),
                                          defaults=except_params)


@after_service_router.get('/{id}', description="a/s get by id",
                          response=AfterServiceListSchema)
def get_after_service_by_id(request, id: int):
    if request.auth.is_staff and request.auth.is_active:
        target = AfterService.objects.get_queryset(id=id)
    else:
        target = AfterService.objects.get_queryset(id=id, user=request.auth)
    queryset = target.select_related('place', 'user')
    return queryset


@after_service_router.put("/", description="a/s 상태 수정")
@admin_permission
def modify_after_service(request, id: int, status: AfterServiceStatus = AfterServiceStatus.APPLY_WAITING):
    target = get_object_or_404(AfterService, id=id, user=request.auth)
    target.status = status
    target.save(update_fields=['status'])


@after_service_router.delete("/", description="a/s 상태 삭제")
def delete_after_service(request, id: int):
    if not request.auth.is_staff:
        obj = get_object_or_404(AfterService, id=id, user=request.auth)
    else:
        obj = get_object_or_404(AfterService, id=id)
    obj.soft_delete()


@refund_router.get("/", description="환불 내역 조회",
                   response=List[RefundListSchema],
                   )
def get_refund_list(request, method: RefundMethod = None, status: RefundStatus = None):
    params = prepare_for_query(request=request)
    if is_admin(request):
        qs = Refund.objects.get_queryset(**params).select_related('order').all()
    else:
        qs = Refund.objects.get_queryset(**params, order__owner=request.auth).select_related('order').all()
    return qs


@refund_router.get("/{id}", description="환불 내역 id로 조회", response=List[RefundListSchema])
def get_refund_list_by_id(request, id: int):
    if is_admin(request):
        qs = Refund.objects.get_queryset(id=id).select_related('order').all()
    else:
        qs = Refund.objects.get_queryset(id=id, order__owner=request.auth).select_related('order').all()
    return qs


@refund_router.post("/", description="환불 내역 생성")
def create_refund_history(request, payload: RefundInsertSchema):
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k not in {'order_id'}}
    order = get_object_or_404(Order, id=params.get('order_id'), deleted_at__isnull=True)
    queryset = Refund.objects.create(order=order, **except_params)


@refund_router.put("/", description="환불 상태 변경, status 가 3일 경우 reject_reason 필수")
@admin_permission
def modify_refund(request, id: int, status: RefundStatus, reject_reason: str = None):
    if status == RefundStatus.REFUSE and reject_reason is None:
        raise RefuseMustHaveReasonException
    target = get_object_or_404(Refund, id=id, order__owner=request.auth, deleted_at__isnull=True)
    target.reject_reason = reject_reason
    target.status = status
    target.save(update_fields=['reject_reason', 'status'])


@refund_router.delete('/', description="환불 내역 삭제")
def delete_refund(request, id: int):
    # params = {'id': id, 'order__owner': request.auth} if is_admin(request) else {id: id}
    # print(Refund.objects.filter(**params))
    if is_admin(request):
        target = get_object_or_404(Refund, id=id)
    else:
        target = get_object_or_404(Refund, id=id, order__owner=request.auth)
    target.soft_delete()


@warranty_router.get('/', description="보증 범위 리스트",
                     response=List[WarrantyListSchema]
                     )
def get_warranty_list(request, is_warranty: bool = True):
    qs = Warranty.objects.get_queryset(is_warranty=is_warranty)
    return qs


@warranty_router.post('/', description="보증 범위 객체 생성 / 수정")
@admin_permission
def create_or_update_warranty(request, payload: WarrantyInsertSchema, id: int = None):
    Warranty.objects.update_or_create(id=id, defaults=payload.dict())


@warranty_router.delete('/', description="보증 범위 객체 삭제")
@admin_permission
def delete_warranty(request, id: int):
    qs = get_object_or_404(Warranty, id=id).soft_delete()
    return qs


@cart_router.get('/', description="장바구니 목록 확인", response=List[CartListSchema])
def get_cart_list(request):
    queryset = Cart.objects.filter(owner=request.auth) \
        .select_related('product_options__product') \
        .annotate(
        product_image=F("product_options__product__productimage__origin_image")
    )
    return queryset


#
# @cart_router.get('/test', description="장바구니 목록 확인", response=List[CartListSchema])
# def get_cart_list_test(request):
#     from django.db.models import F
#     queryset = Cart.objects.filter(owner=request.auth)\
#         .select_related('product_options__product')\
#         .annotate(
#         product_image=F("product_options__product__productimage__origin_image")
#     )
#     return queryset


@cart_router.post('/', description="장바구니 목록 생성")
def create_cart(request, payload: CartCreateSchema):
    product_options_id = payload.dict()['product_options_id']
    amount = payload.dict()['amount']
    queryset = Cart.objects.create(
        product_options=get_object_or_404(ProductOptions, id=product_options_id),
        owner=request.auth,
        amount=amount
    )


@cart_router.delete('/', description="장바구니 삭제")
def delete_cart(request, id: int):
    queryset = get_object_or_404(Cart, id=id, owner=request.auth).delete()
    return queryset
