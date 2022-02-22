from datetime import date, datetime
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, File, Router
from ninja.responses import Response

from conf.message import REFUSE_MUST_HAVE_REASON
from history.constant import AfterServiceStatus, RefundMethod, RefundStatus, BatteryExchangeSort
from history.models import AfterService, Refund, Warranty, BatteryExchange
from history.schema import AfterServiceInsertSchema, RefundInsertSchema, WarrantyInsertSchema, \
    BatteryExchangeInsertSchema
from member.models import MemberOwnedVehicles
from order.models import Order, IntegratedFeePlan
from placement.models import Placement
from util.default import ResponseDefaultHeader
from util.number import generate_random_number
from util.params import prepare_for_query

history_router = Router()
refund_router = Router()
after_service_router = Router()
warranty_router = Router()
battery_router = Router()


@after_service_router.get("/", description="a/s 내역 보기", response=ResponseDefaultHeader.Schema)
def get_after_service_list(request, id: int = None, status: AfterServiceStatus = None, is_created__gte: date = None,
                           is_created__lte: date = None):
    params = prepare_for_query(request=request)
    qs = AfterService.objects.filter(**params).select_related('place', 'vehicle').all()
    print(qs.values())
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs.values()
    )


@after_service_router.post("/", description="a/s 내역 생성", response=ResponseDefaultHeader.Schema)
def create_after_service_history(request, payload: AfterServiceInsertSchema):
    place = get_object_or_404(Placement, id=payload.dict()['place_id'])
    member = get_object_or_404(Placement, id=payload.dict()['member_id'])
    query_set = AfterService.objects.create(
        place=place,
        owner=member,
        registration_number=generate_random_number(),
        reservation_date=payload.dict()['reservation_date'],
        detail=payload.dict()['detail'],
        category=payload.dict()['category'],
    )
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=query_set
    )


@after_service_router.put("/", description="a/s 상태 수정", response=ResponseDefaultHeader.Schema)
def change_after_service_status(request, id: int, status: AfterServiceStatus):
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=AfterService.objects.filter(id=id).update(status=status)
    )


@refund_router.get("/", description="환불 내역 조회", response=ResponseDefaultHeader.Schema)
def get_refund_list(request, method: RefundMethod = None, status: RefundStatus = None):
    params = prepare_for_query(request=request)
    qs = Refund.objects.filter(**params).select_related('order').all()

    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs.values()
    )


@refund_router.post("/", description="환불 내역 생성", response=ResponseDefaultHeader.Schema)
def create_refund_history(request, payload: RefundInsertSchema):
    payload_copy = payload.copy().dict()
    qs = Refund.objects.create(
        order=get_object_or_404(Order, id=payload_copy['order_id']),
        reject_reason=payload_copy['reject_reason'],
        method=payload_copy['method'],
        status=payload_copy['status'],
    )
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs.values()
    )


@refund_router.put("/", description="환불 상태 변경, status 가 3일 경우 reject_reason 필수", response=ResponseDefaultHeader.Schema)
def modify_refund(request, id: int, status: RefundStatus, reject_reason: str = None):
    if status == RefundStatus.REFUSE and reject_reason is None:
        raise Exception(REFUSE_MUST_HAVE_REASON)
    params = prepare_for_query(request=request)
    query_set = get_object_or_404(Refund, id=id).objects.update(**params)
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=query_set
    )


@warranty_router.get('/', description="보증 범위 리스트", response=ResponseDefaultHeader.Schema)
def get_warranty_list(request):
    params = prepare_for_query(request)
    qs = Warranty.objects.filter(**params).all()
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs
    )


@warranty_router.post('/', description="보증 범위 객체 생성", response=ResponseDefaultHeader.Schema)
def create_warranty(request, payload: WarrantyInsertSchema):
    qs = Warranty.objects.create(**payload.dict())
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs
    )


@warranty_router.put('/', description="보증 범위 수정", response=ResponseDefaultHeader.Schema)
def modify_warranty(request, id: int, validity: datetime = None):
    params = prepare_for_query(request)
    qs = get_object_or_404(Warranty, id=id).update(**params)
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs
    )


@warranty_router.delete('/', description="보증 범위 객체 삭제", response=ResponseDefaultHeader.Schema)
def delete_warranty(request, id: int):
    qs = get_object_or_404(Warranty, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=qs
    )


@battery_router.get('/', description="배터리 교환 내역 조회")
def get_battery_exchange_history(request, sort: BatteryExchangeSort = None):
    # [정렬] -  { 최근 지불 일정, 늦은 지불 일정, 높은 요금 순, 낮은 요금 순 , 누적 사용량 높은 순 , 누적 사용량 낮은 순 }
    params = prepare_for_query(request=request, exceptions=['sort'])
    field_name = 'order__is_created'
    if sort == BatteryExchangeSort.RECENT_PAYMENT_DATE:
        field_name == 'is_created'
    elif sort == BatteryExchangeSort.LATEST_PAYMENT_DATE:
        field_name == '-is_created'
    elif sort == BatteryExchangeSort.HIGH_PAYMENT:  # todo 나이스페이 관련 작업 후 변경
        field_name == '-order__is_created'
    elif sort == BatteryExchangeSort.LOW_PAYMENT:
        field_name == '-order__is_created'
    elif sort == BatteryExchangeSort.HIGH_USED_BATTERY:
        field_name == 'used_battery'
    elif sort == BatteryExchangeSort.LOW_USED_BATTERY:
        field_name == '-used_battery'
    else:
        field_name = 'order__is_created'

    queryset = BatteryExchange.objects.filter(**params).select_related('place', 'order', 'member_vehicle',
                                                                       'fee_plan').order_by(field_name)
    return queryset


@battery_router.post('/', description="배터리 교환 내역 생성", response=ResponseDefaultHeader.Schema)
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
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=queryset
    )


@battery_router.delete('/', description="배터리 교환 내역 삭제", response=ResponseDefaultHeader.Schema)
def delete_battery_history(request, id: int):
    queryset = get_object_or_404(BatteryExchange, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        data=queryset
    )
