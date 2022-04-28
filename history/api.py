from datetime import date, datetime
from typing import List

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ninja import Router

from conf.custom_exception import RefuseMustHaveReasonException
from history.constant import AfterServiceStatus, RefundMethod, RefundStatus, BatteryExchangeSort
from history.models import AfterService, Refund, Warranty, BatteryExchange, Cart
from history.schema import AfterServiceInsertSchema, RefundInsertSchema, WarrantyInsertSchema, \
    BatteryExchangeInsertSchema, CartListSchema, CartCreateSchema, AfterServiceListSchema, RefundListSchema, \
    WarrantyListSchema
from member.models import MemberOwnedVehicles
from order.models import Order, IntegratedFeePlan
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
@after_service_router.get("/", description="a/s 특정한 내역")
def get_after_service_list(request, status: AfterServiceStatus = None, is_created__gte: date = None,
                           is_created__lte: date = None):
    params = prepare_for_query(request=request)
    queryset = AfterService.objects.get_queryset(**params).select_related('place', 'vehicle', 'user')
    return queryset


@login_required
@after_service_router.get('/{id}', description="a/s get by id",
                          auth=None,
                          response=AfterServiceListSchema)
def get_after_service_by_id(request, id: int):
    queryset = AfterService.objects.get_queryset(id=id, user=request.user).select_related('place', 'vehicle', 'user')
    return queryset


@login_required
@after_service_router.post("/", description="a/s 내역 생성")
def create_after_service_history(request, payload: AfterServiceInsertSchema):
    user = request.user
    # if not user.is_superuser:
    #     raise AccessDeniedException
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k in {'place_id', 'owned_vehicle_id'}}
    place = Placement.objects.get_queryset(id=params.get('place_id'))
    owned_vehicle = MemberOwnedVehicles.objects.get_queryset(id=params.get('vehicle_id'))
    queryset = AfterService.objects.create(user=user, place=place, owned_vehicle=owned_vehicle, **except_params)
    return queryset


@login_required
@after_service_router.put("/", description="a/s 상태 수정")
def modify_after_service(request, id: int, payload: AfterServiceInsertSchema):
    obj = get_object_or_404(AfterService, id=id, user=request.user)
    queryset = obj.objects.update(**payload.dict())
    obj.save()
    return queryset


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
def get_warranty_list(request):
    params = prepare_for_query(request)
    qs = Warranty.objects.get_queryset(**params)
    return qs


@warranty_router.post('/', description="보증 범위 객체 생성")
def create_warranty(request, payload: WarrantyInsertSchema):
    qs = Warranty.objects.create(**payload.dict())
    return qs


@warranty_router.put('/', description="보증 범위 수정")
def modify_warranty(request, id: int, validity: datetime = None):
    params = prepare_for_query(request)
    qs = get_object_or_404(Warranty, id=id, deleted_at__isnull=True).objects.update(**params)
    return qs


@warranty_router.delete('/', description="보증 범위 객체 삭제")
def delete_warranty(request, id: int):
    qs = get_object_or_404(Warranty, id=id).soft_delete()
    return qs


@login_required
@battery_router.get('/', description="배터리 교환 내역 조회")
def get_battery_exchange_history_list(request, sort: BatteryExchangeSort = None):
    # [정렬] -  { 최근 지불 일정, 늦은 지불 일정, 높은 요금 순, 낮은 요금 순 , 누적 사용량 높은 순 , 누적 사용량 낮은 순 }
    params = prepare_for_query(request=request, exceptions=['sort'])
    if sort == BatteryExchangeSort.RECENT_PAYMENT_DATE:
        field_name = 'is_created'
    elif sort == BatteryExchangeSort.LATEST_PAYMENT_DATE:
        field_name = '-is_created'
    elif sort == BatteryExchangeSort.HIGH_PAYMENT:  # todo 나이스페이 관련 작업 후 변경
        field_name = '-order__is_created'
    elif sort == BatteryExchangeSort.LOW_PAYMENT:
        field_name = '-order__is_created'
    elif sort == BatteryExchangeSort.HIGH_USED_BATTERY:
        field_name = 'used_battery'
    elif sort == BatteryExchangeSort.LOW_USED_BATTERY:
        field_name = '-used_battery'
    else:
        field_name = 'order__is_created'

    queryset = BatteryExchange.objects.get_queryset(**params).select_related('place', 'order', 'member_vehicle',
                                                                             'fee_plan').order_by(field_name)

    return queryset


@login_required
@battery_router.get('/user', description="배터리 교환 내역 조회")
def get_battery_exchange_history_by_user(request):
    order = get_object_or_404(Order, deleted_at__isnull=True, owner=request.user)
    queryset = BatteryExchange.objects.get_queryset(order=order).select_related('place', 'order', 'member_vehicle',
                                                                                'fee_plan')
    return queryset


@battery_router.post('/', description="배터리 교환 내역 생성")
def create_battery_history(request, payload: BatteryExchangeInsertSchema):
    params = payload.dict()
    place = get_object_or_404(Placement, id=params['place_id'])
    order = get_object_or_404(Order, id=params['order_id'])
    member_owned_vehicles = get_object_or_404(MemberOwnedVehicles, id=params['member_owned_vehicles_id'])
    fee_plan = get_object_or_404(IntegratedFeePlan, params['fee_plan_id'])
    queryset = BatteryExchange.objects.update_or_create(
        place=place,
        order=order,
        member_vehicle=member_owned_vehicles,
        fee_plan=fee_plan,
        used_battery=params['used_battery'],
    )
    return queryset


@battery_router.delete('/', description="배터리 교환 내역 삭제")
def delete_battery_history(request, id: int):
    queryset = get_object_or_404(BatteryExchange, id=id).soft_delete()
    return queryset


@login_required
@cart_router.get('/', description="장바구니 목록 확인", response={200: List[CartListSchema]})
def get_cart_list(request):
    queryset = Cart.objects.get_queryset(owner=request.user, deleted_at__isnull=True).select_related(
        'product')
    return queryset


@login_required
@cart_router.post('/', description="장바구니 목록 생성")
def create_cart_list(request, payload: CartCreateSchema):
    product_id = payload.dict()['product_id']
    amount = payload.dict()['amount']
    queryset = Cart.objects.create(
        product=get_object_or_404(Product, id=product_id),
        owner=request.user,
        amount=amount
    )
    return queryset


@login_required
@cart_router.delete('/', description="장바구니 삭제")
def delete_cart(request, id: int):
    queryset = get_object_or_404(Cart, id=id).delete()
    return queryset
