from datetime import date
from typing import List

from django.db import transaction
from django.db.models import Prefetch, F
from django.shortcuts import get_object_or_404
from ninja import Router

from conf.custom_exception import RefuseMustHaveReasonException, UserNotAccessDeniedException, WrongParameterException
from history.constant import AfterServiceStatus, RefundMethod, RefundStatus
from history.models import AfterService, Refund, Warranty, Cart, RefundLocation, PrevEstimate, InternalCombustionEngine, \
    Expendables, FuelRateByVehicleType, VehicleInfo
from history.schema import AfterServiceInsertSchema, RefundInsertSchema, WarrantyInsertSchema, CartListSchema, \
    CartCreateSchema, AfterServiceListSchema, RefundListSchema, \
    WarrantyListSchema, PrevEstimateCreateSchema, PrevEstimateListSchema
from order.models import Order
from placement.models import Placement
from product.models import ProductOptions
from util.number import generate_after_service_number
from util.params import prepare_for_query
from util.permission import is_admin

refund_router = Router()
after_service_router = Router()
warranty_router = Router()
battery_router = Router()
cart_router = Router()
prev_estimate_router = Router()


@after_service_router.get("/", response=List[AfterServiceListSchema])
def get_after_service_list(request, status: AfterServiceStatus = None, is_created__gte: date = None,
                           is_created__lte: date = None):
    """
    A/S 리스트 API
    - :param status:     APPLY_WAITING(접수 대기) = 0
    APPLY_COMPLETED(접수 완료) = 1
    ON_PROGRESS(처리 중) = 2
    PROGRESS_COMPLETED(처리 완료) = 3
    - :param is_created__gte: 기간 지정 검색, 해당 파라 미터 보다 미래 값이 도출 된다.
    - :param is_created__lte: 기간 지정 검색, 해당 파라 미터 보다 과거 값이 도출 된다.
    """
    params = prepare_for_query(request=request)
    if is_admin(request.auth):
        target = AfterService.objects.get_queryset(**params)
    else:
        target = AfterService.objects.get_queryset(**params, user=request.auth)
    queryset = target.select_related('place', 'user')
    return queryset


@after_service_router.post("/", description="a/s 내역 생성 / 수정")
def update_or_create_after_service_history(request, payload: AfterServiceInsertSchema):
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k in {'place_id'}}
    except_params['registration_number'] = generate_after_service_number()
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


@after_service_router.put("/")
def modify_after_service(request, id: int, status: AfterServiceStatus = AfterServiceStatus.APPLY_WAITING):
    """
    a/s 상태 수정
    - :param id: A/S 아이디
    - :param status:     APPLY_WAITING(접수 대기) = 0
    APPLY_COMPLETED(접수 완료) = 1
    ON_PROGRESS(처리 중) = 2
    PROGRESS_COMPLETED(처리 완료) = 3
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    target = get_object_or_404(AfterService, id=id, user=request.auth)
    target.status = status
    target.save(update_fields=['status'])


@after_service_router.delete("/", description="a/s 삭제")
def delete_after_service(request, id: int):
    if not request.auth.is_staff:
        obj = get_object_or_404(AfterService, id=id, user=request.auth)
    else:
        obj = get_object_or_404(AfterService, id=id)
    obj.soft_delete()


@refund_router.get("/",
                   response=List[RefundListSchema]
                   )
def get_refund_list(request, method: RefundMethod = None, status: RefundStatus = None):
    """
    환불 내역 조회
    - :param method:
    RECALL_REQUEST(회수 요청) = 0,
    DIRECT (직접 발송)= 1
    - :param status:
    WAITING(환불 대기) = 0
    COMPLETED(환불 완료) = 1
    ACCEPTED(환불 수락) = 2
    REFUSE(환불 거절) = 3
    """
    params = prepare_for_query(request=request)
    if is_admin(request.auth):
        qs = Refund.objects.get_queryset(**params).select_related('order').all()
    else:
        qs = Refund.objects.get_queryset(**params, order__owner=request.auth).select_related('order').all()
    return qs


@refund_router.get("/{id}", description="환불 내역 id로 조회", response=List[RefundListSchema])
def get_refund_list_by_id(request, id: int):
    if is_admin(request.auth):
        qs = Refund.objects.get_queryset(id=id).select_related('order').all()
    else:
        qs = Refund.objects.get_queryset(id=id, order__owner=request.auth).select_related('order').all()
    return qs


@refund_router.post("/", description="환불 내역 생성")
def create_refund_history(request, payload: RefundInsertSchema):
    params = payload.dict()
    except_params = {k: v for k, v in params.items() if k not in {'order_id', 'refund_location'}}
    refund_location_params = params['refund_location']

    order = get_object_or_404(Order, id=params.get('order_id'), deleted_at__isnull=True)
    refund_location = RefundLocation.objects.create(**refund_location_params)
    queryset = Refund.objects.create(order=order, refund_location=refund_location, **except_params)


@refund_router.put("/")
def modify_refund(request, id: int, status: RefundStatus, reject_reason: str = None):
    """
    환불 상태 변경 API, status 가 3일 경우 reject_reason 필수
    - :param id: 환불 아이디
    - :param status: 환불 상태
    WAITING(환불 대기) = 0
    COMPLETED(환불 완료) = 1
    ACCEPTED(환불 수락) = 2
    REFUSE(환불 거절) = 3
    - :param reject_reason: 환불 사유, 환불 거절 상태일 때 필수 값
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    if status == RefundStatus.REFUSE and reject_reason is None:
        raise RefuseMustHaveReasonException
    target = get_object_or_404(Refund, id=id, order__owner=request.auth, deleted_at__isnull=True)
    target.reject_reason = reject_reason
    target.status = status
    target.save(update_fields=['reject_reason', 'status'])


@refund_router.delete('/', description="환불 내역 삭제")
def delete_refund(request, id: int):
    if is_admin(request.auth):
        target = get_object_or_404(Refund, id=id)
    else:
        target = get_object_or_404(Refund, id=id, order__owner=request.auth)
    target.soft_delete()


@warranty_router.get('/',
                     response=List[WarrantyListSchema])
def get_warranty_list(request, is_warranty: bool = True):
    """
    보증 범위에 관현 리스트를 가져 오는 API
    -   :param is_warranty: 보증 범위 적용 여부
    """
    qs = Warranty.objects.get_queryset(is_warranty=is_warranty)
    return qs


@warranty_router.post('/')
def create_or_update_warranty(request, payload: WarrantyInsertSchema, id: int = None):
    """
    보증 범위 객체 생성 / 수정
    -   :param id: 수정일 경우 id를 파라 미터로 넘겨 줘야 함.
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    Warranty.objects.update_or_create(id=id, defaults=payload.dict())


@warranty_router.delete('/', description="보증 범위 객체 삭제")
def delete_warranty(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    qs = get_object_or_404(Warranty, id=id).soft_delete()
    return qs


@cart_router.get('/', description="장바구니 목록 확인", response=List[CartListSchema])
def get_cart_list(request):
    queryset = Cart.objects.annotate(product_image=F("product_options__product__productimage__origin_image")).select_related('product_options__product')
    return queryset


@cart_router.post('/', description="장바구니 목록 생성")
def create_cart(request, payload: CartCreateSchema):
    product_options_id = payload.dict()['product_options_id']
    amount = payload.dict()['amount']
    queryset = Cart.objects.create(
        product_options=get_object_or_404(ProductOptions, id=product_options_id),
        owner=request.auth,
        amount=amount
    )


@cart_router.delete('/')
def delete_cart(request, id: int = None, is_delete_all: bool = False):
    '''
    :param id: 카트 아이디
    :param is_delete_all: 전체 삭제 기능 default는 False 이며, True 시 유저가 갖고 있는 전체 장 바구니 목록을 가져 와서 삭제 한다.
    :return:
    '''
    if is_delete_all:
        target = Cart.objects.filter(owner=request.auth)
        target.delete()
    else:
        if id and id > 0:
            target = get_object_or_404(Cart, id=id, owner=request.auth)
            target.delete()
        else:
            raise WrongParameterException


@prev_estimate_router.get('/', response=List[PrevEstimateListSchema])
def get_prev_estimate(request):
    """
        가견적 가져 오는 API
    """
    queryset = PrevEstimate.objects.filter().prefetch_related(
        Prefetch('vehicleinfo', queryset=VehicleInfo.objects.prefetch_related(
            Prefetch('fuelratebyvehicletype_set', to_attr='fuel_rate_by_vehicle_type')), to_attr='vehicle_info'),
        Prefetch('internalcombustionengine_set', to_attr='internal_combustion_engine'),
        Prefetch('expendables_set', to_attr='expendables_list'),
    )
    return queryset


@transaction.atomic(using='default')
@prev_estimate_router.post('/')
def update_or_create_prev_estimate(request, payload: PrevEstimateCreateSchema):
    """
    가견적 관리 생성 및 수정
    """
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException

    params = payload.dict()
    vehicle_info: dict = params['vehicle_info']
    expendables = params['expendables']
    internal_combustion_engine = params['internal_combustion_engine']
    fuel_rate_by_vehicle_type = vehicle_info['fuel_rate_by_vehicle_type']
    vehicle_info_except_vt = {k: v for k, v in vehicle_info.items() if k not in {'fuel_rate_by_vehicle_type'}}

    try:
        with transaction.atomic():
            count = len(PrevEstimate.objects.filter())
            if count > 1:
                raise Exception("asdasd")

            if count == 0:
                prev_estimate = PrevEstimate.objects.create()
            else:
                prev_estimate = PrevEstimate.objects.all().first()
                # 업데이트 전 초기화
                prev_estimate.vehicleinfo.delete()
                for ice_set in prev_estimate.internalcombustionengine_set.all():
                    ice_set.delete()

                for ex_set in prev_estimate.expendables_set.all():
                    ex_set.delete()

            if vehicle_info:
                created_vi = VehicleInfo.objects.create(**vehicle_info_except_vt, prev_estimate=prev_estimate)
                if fuel_rate_by_vehicle_type:
                    for vt in fuel_rate_by_vehicle_type:
                        FuelRateByVehicleType.objects.create(**vt, vehicle_info=created_vi)

            if internal_combustion_engine:
                for ice in internal_combustion_engine:
                    created_ice = InternalCombustionEngine.objects.create(**ice, prev_estimate=prev_estimate)

            if expendables:
                for ex in expendables:
                    created_ex = Expendables.objects.create(**ex, prev_estimate=prev_estimate)

    except Exception as e:
        raise e