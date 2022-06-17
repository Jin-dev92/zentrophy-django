from typing import List

import requests
from asgiref.sync import sync_to_async
from django.db import transaction
from django.db.models import F
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import AlreadyExistsException, WrongParameterException, \
    NotEnoughStockException, UserNotAccessDeniedException, OrderStateCantChangeException, IncorrectTotalAmountException, \
    MustHaveDeliveryToException, IncorrectOrderStateException
from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, REQUEST_PAYMENT
from order.constant import OrderState, DeliveryMethod
from order.models import Order, Subside, DocumentFile, ExtraSubside, OrderedProductOptions, OrderedVehicleColor, \
    OrderLocationInfo, CustomerInfo, DocumentFormat, Subscriptions, DeliveryTo
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema, \
    DocumentFormatListSchema, SubscriptionsCreateSchema, RequestPaymentSubscriptionsSchema, \
    RequestPaymentSubscriptionsScheduleSchema, ApplySubSideSchema, DeliveryMethodInputSchema
from product.models import ProductOptions, VehicleColor
from util.number import check_invalid_product_params
from util.permission import is_admin

router = Router()
subside_router = Router()
file_router = Router()
subscription_router = Router()

upload_exceed_count = 5


@router.get('/', response=List[OrderListSchema], description="주문 검색")
def get_order_list(request):
    if is_admin(request.auth):
        target = Order.objects.get_queryset()
    else:
        target = Order.objects.get_queryset(owner=request.auth)

    queryset = target.prefetch_related(
        'customer_info',
        'order_location_info',
        Prefetch(lookup='orderedproductoptions_set',
                 queryset=OrderedProductOptions.objects.select_related('product_options')
                 .annotate(product_image=F('product_options__product__productimage__origin_image')),
                 to_attr="ordered_product_options"),
        Prefetch(lookup='orderedvehiclecolor_set',
                 queryset=OrderedVehicleColor.objects.select_related('vehicle_color')
                 .prefetch_related(Prefetch('vehicle_color__vehicleimage_set', to_attr='vehicle_image')),
                 to_attr="ordered_vehicle_color"),
        Prefetch(lookup='documentfile_set', to_attr="files"),
    )
    return queryset


@router.get('/{id}', description="주문 id로 검색", response=List[OrderListSchema])
def get_order_list_by_id(request, id: int):
    if is_admin(request.auth):
        target = Order.objects.get_queryset(id=id)
    else:
        target = Order.objects.get_queryset(id=id, owner=request.auth)

    queryset = target.prefetch_related(
        'customer_info',
        'order_location_info',
        Prefetch(lookup='orderedproductoptions_set',
                 queryset=OrderedProductOptions.objects.select_related('product_options')
                 .annotate(product_image=F('product_options__product__productimage__origin_image')),
                 to_attr="ordered_product_options"),
        Prefetch(lookup='orderedvehiclecolor_set',
                 queryset=OrderedVehicleColor.objects.select_related('vehicle_color')
                 .prefetch_related(Prefetch('vehicle_color__vehicleimage_set', to_attr='vehicle_image')),
                 to_attr="ordered_vehicle_color"),
        Prefetch(lookup='documentfile_set', to_attr="files"),
    )
    return queryset


@router.post('/delivery_method/{id}', description="배달 정보 입력")
def delivery_method_input(request, id: int, payload: DeliveryMethodInputSchema):
    params = payload.dict()
    delivery_method = params['delivery_method']
    delivery_to: dict = params['delivery_to']
    place_remote_pk = params['place_remote_pk']

    if delivery_method == DeliveryMethod.DEPEND_ON and not delivery_to:
        raise MustHaveDeliveryToException
    if delivery_method == DeliveryMethod.YOURSELF and not place_remote_pk:
        raise MustHaveDeliveryToException

    target = get_object_or_404(Order, id=id, owner=request.auth)
    target.delivery_method = delivery_method
    if delivery_method == DeliveryMethod.DEPEND_ON:
        target.delivery_to = DeliveryTo.objects.create(**delivery_to)
    else:
        target.place_remote_pk = place_remote_pk

    target.save(update_fields=['delivery_method', 'delivery_to', 'place_remote_pk'])


@router.post('/apply_subsides/{id}', description="주문 보조금 적용")
def apply_subsides_to_order(request, payload: ApplySubSideSchema, id: int):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    try:
        discount = 0    # 1대당 할인 금액

        target = get_object_or_404(Order, id=id)
        extra_bulk = ExtraSubside.objects.in_bulk(id_list=payload.dict()['extra_subside'])
        # 1대당 할인 금액 계산
        for ordered_vehicle in target.orderedvehiclecolor_set.all():
            if ordered_vehicle.vehicle_color.vehicle.able_subsidy and target.customer_info.is_apply_subside:   # 기본 보조금 계산
                discount += Subside.objects.all().first().amount * ordered_vehicle.amount

            if ordered_vehicle.vehicle_color.vehicle.able_extra_subsidy and target.customer_info.is_apply_subside:
                for extra_id in extra_bulk:
                    discount += ExtraSubside.objects.get(id=extra_id).amount * ordered_vehicle.amount

        target.total -= discount
        target.discount_total = discount
        if target.total < 0:
            target.total = 0
        target.save(update_fields=['total', 'discount_total'])

    except Exception as e:
        raise e


@router.post('/is_request_submit/{id}', description="서류 재접수 토글")
def change_is_request_submit(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    target = get_object_or_404(Order, id=id)
    if target.state != OrderState.REVIEW_DOCS:
        raise IncorrectOrderStateException
    target.is_request_submit = not target.is_request_submit
    target.save(update_fields=['is_request_submit'])


@router.post('/is_delivery/{id}', description="출고준비 -> 배송중, 배송중 -> 출고 준비 상태 토글")
def change_is_delivery(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException

    target = get_object_or_404(Order, id=id)
    if target.state != OrderState.PREPARE_DELIVERY:
        raise IncorrectOrderStateException

    target.is_delivery = not target.is_delivery
    target.save(update_fields=['is_delivery'])


@transaction.atomic(using='default')
@router.post('/', description="주문 생성 / 수정")
def update_or_create_order(request, payload: OrderCreateSchema, id: int = None):
    if not is_admin(request.auth) and (id and id > -1):  # 일반 유저가 id 를 보냈을 경우에 예외 처리 해준다.
        raise UserNotAccessDeniedException
    try:
        with transaction.atomic():
            params = payload.dict()
            order_params = {k: v for k, v in params.items() if
                            k not in {'ordered_product_options', 'ordered_vehicle_color', 'extra_subside',
                                      'customer_info',
                                      'order_location_info'}}
            order_location_info_params = params['order_location_info']
            customer_info_params = params['customer_info']
            extra_subside_params: list = params.get('extra_subside')

            ordered_vehicle_color = params['ordered_vehicle_color']
            ordered_product_options = params['ordered_product_options']
            total = params['total']

            if id and id > -1:  # 수정 로직 수행 전 데이터 세팅
                target = get_object_or_404(Order, id=id)
                # 수정이면 갖고 있던 foreign_key 데이터를 삭제한다.
                target.extra_subside.remove()
                target.customer_info.delete()
                target.order_location_info.delete()
                target.orderedproductoptions_set.all().delete()
                target.orderedvehiclecolor_set.all().delete()
                order_params['owner'] = target.owner
            else:   # 생성 로직 수행 전 데이터 세팅
                target = None
                order_params['owner'] = request.auth

            customer_object = CustomerInfo.objects.update_or_create(order=target, defaults=customer_info_params)
            location_object = OrderLocationInfo.objects.update_or_create(order=target, defaults=order_location_info_params)

            order_params['customer_info'] = customer_object[0]
            order_params['order_location_info'] = location_object[0]

            order_queryset = Order.objects.update_or_create(id=id, defaults=order_params)  # 주문 생성

            if extra_subside_params and len(extra_subside_params) > 0 and extra_subside_params.count(0) == 0:
                order_queryset[0].extra_subside.add(
                    *ExtraSubside.objects.in_bulk(id_list=params.get('extra_subside')))  # manytomany field

            if ordered_product_options and len(ordered_product_options) > 0:    #   주문한 상품이 존재할 경우
                if not check_invalid_product_params(ordered_product_options):     # 파라미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                acc_total = 0   # 가격 검증을 위한 변수
                for index, po in enumerate(ordered_product_options):    # 상품 주문 생성 시 판매량, 재고량 조절
                    po_target = get_object_or_404(ProductOptions, id=po.get('product_options_id'))
                    acc_total += po_target.product.product_price * po.get('amount')
                    if po.get('amount') > po_target.stock_count:
                        raise NotEnoughStockException
                    po_target.sale_count = po_target.sale_count + po.get('amount')
                    po_target.stock_count = po_target.stock_count - po.get('amount')
                    po_target.save(update_fields=['sale_count', 'stock_count'])

                if total != acc_total:  # 가격 검증의 결과와 요청한 금액이 맞지 않을 때 에러를 띄워 준다.
                    raise IncorrectTotalAmountException

                po_list = OrderedProductOptions.objects.bulk_create(
                    objs=[
                        OrderedProductOptions(**ordered_po,
                                              order=order_queryset[0])
                        for ordered_po in ordered_product_options]
                )

            elif ordered_vehicle_color and len(ordered_vehicle_color) > 0:  #   주문한 모터 사이클이 존재할 경우
                if not check_invalid_product_params(ordered_vehicle_color): # 파라 미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                acc_total = 0   # 가격 검증을 위한 변수
                for index, vc in enumerate(ordered_vehicle_color):  # 모터 사이클 주문 생성시 판매량, 재고량 조절
                    vc_target = get_object_or_404(VehicleColor, id=vc.get('vehicle_color_id'))
                    acc_total += vc_target.price * vc.get('amount')
                    if vc.get('amount') > vc_target.stock_count:
                        raise NotEnoughStockException
                    vc_target.sale_count = vc_target.sale_count + vc.get('amount')
                    vc_target.stock_count = vc_target.stock_count - vc.get('amount')
                    vc_target.save(update_fields=['sale_count', 'stock_count'])

                if total != acc_total:  # 가격 검증의 결과와 요청한 금액이 맞지 않을 때 에러를 띄워 준다.
                    raise IncorrectTotalAmountException

                vc_list = OrderedVehicleColor.objects.bulk_create(
                    objs=[OrderedVehicleColor(**ordered_vc, order=order_queryset[0]) for ordered_vc in ordered_vehicle_color])

            else:
                raise WrongParameterException

    except Exception as e:
        raise e


@router.put('/', description="주문 상태 수정, OrderListSchema - state 주석 참조")
def change_order_state(request, id: int, state: OrderState):
    # orderState가 3일 경우 유저 접근 가능하도록.
    if not is_admin(request.auth):  # 어드민 접근 제한
        if state != OrderState.PREPARE_DELIVERY:
            raise UserNotAccessDeniedException

    try:
        target = get_object_or_404(Order, id=id)
        if target.state == OrderState.IS_CANCELED:
            raise OrderStateCantChangeException
        if target.state > OrderState.REVIEW_DOCS and target.is_request_submit:
            target.is_request_submit = False
        if state == OrderState.PREPARE_DELIVERY:
            target.is_delivery = False   # 출고 준비 중

        target.state = state
        target.save(update_fields=['state', 'is_request_submit'])

        if OrderState.IS_CANCELED:  # 주문 취소 하였을 때 재고량과 판매량을 원복 해줘야 한다.
            ordered_product_options = target.orderedproductoptions_set.all()
            ordered_vehicle_colors = target.orderedvehiclecolor_set.all()

            if len(ordered_product_options) > 0:
                for ordered_product_option in ordered_product_options:
                    amount = ordered_product_option.amount
                    ordered_product_option.product_options.stock_count += amount
                    ordered_product_option.product_options.sale_count -= amount

                    if ordered_product_option.product_options.sale_count < 0:
                        ordered_product_option.product_options.sale_count = 0
                    ordered_product_option.product_options.save(update_fields=['stock_count', 'sale_count'])

            elif len(ordered_vehicle_colors) > 0:
                for ordered_vehicle_color in ordered_vehicle_colors:
                    amount = ordered_vehicle_color.amount
                    ordered_vehicle_color.vehicle_color.stock_count += amount
                    ordered_vehicle_color.vehicle_color.sale_count -= amount

                    if ordered_vehicle_color.vehicle_color.sale_count < 0:
                        ordered_vehicle_color.vehicle_color.sale_count = 0
                    ordered_vehicle_color.vehicle_color.save(update_fields=['stock_count', 'sale_count'])

    except Exception as e :
        raise e


@router.delete('/', description="주문 삭제")
def delete_order_list_by_id(request, id: int):
    target = get_object_or_404(Order, id=id)
    queryset = target.soft_delete()


@subside_router.get('/', response=List[SubsideListSchema])
def get_list_subside(request):
    queryset = Subside.objects.get_queryset().prefetch_related(
        Prefetch('extrasubside_set', to_attr="extra")
    )
    return queryset


@transaction.atomic(using='default')
@subside_router.post('/')
def create_subside(request, payload: SubsideInsertSchema):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    subside_amount = len(Subside.objects.all())
    try:
        with transaction.atomic():
            if subside_amount == 0:
                subside = Subside.objects.create(amount=payload.dict().get('amount'))
            else:
                raise AlreadyExistsException
            extra_list = [ExtraSubside(**item, subside=subside) for item in payload.dict().get('extra')]
            ExtraSubside.objects.bulk_create(objs=extra_list)

    except Exception as e:
        raise e

    return True


@subside_router.put('/', description="기본 보조금 수정")
def modify_subside(request, payload: SubsideInsertSchema = None):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    for extra_subside in ExtraSubside.objects.get_queryset():
        extra_subside.soft_delete()
    if payload:
        subside = Subside.objects.all().first()
        subside.amount = payload.amount
        subside.save(update_fields=['amount'])
        extra_list = [ExtraSubside(**item, subside=subside) for item in payload.dict().get('extra')]
        queryset = ExtraSubside.objects.bulk_create(objs=extra_list)
    return True


@file_router.post('/', description="계획서 및 보조금 신청서 업로드")
def upload_files(request, order_id: int, files: List[UploadedFile]):
    order = get_object_or_404(Order, id=order_id)
    if order.state == OrderState.REVIEW_DOCS and order.is_request_submit:
        order.is_request_submit = False
    queryset = DocumentFile.objects.bulk_create(
        objs=[DocumentFile(order=order, file=file) for file in files], batch_size=upload_exceed_count)


@file_router.delete('/', description="계획서 및 보조금 신청서 삭제")
def delete_files(request, id: int):
    queryset = get_object_or_404(DocumentFile, id=id).delete()


@file_router.get('/format', description="보조금 신청서 포맷 리스트", response=List[DocumentFormatListSchema])
def get_format_list(request):
    queryset = DocumentFormat.objects.get_queryset()
    return queryset


@file_router.post('/format', description="보조금 신청서 포맷 업로드")
def upload_format_files(request, file: UploadedFile):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    queryset = DocumentFormat.objects.create(file=file)


@file_router.delete('/format', description="보조금 신청서 포맷 삭제")
# @admin_permission
def delete_format_files(request, id: int):
    if not is_admin(request.auth):  # 어드민 접근 제한
        raise UserNotAccessDeniedException
    target = get_object_or_404(DocumentFormat, id=id)
    queryset = target.soft_delete()


@sync_to_async
@subscription_router.post('/issue_billing', description="나이츠 페이먼츠 정기 결제")
def create_subscription(request, payload: SubscriptionsCreateSchema):
    params = payload.dict()
    data = {k: v for k, v in payload.dict().items() if k not in {'customer_uid'}}
    try:
        token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
        token_response_json = token_response.json()
        if int(token_response_json['code']) == 0:
            access_token = token_response_json['response'].get('access_token')
            issue_billing_response = requests.post(
                url=ISSUE_BILLING_INFO['url'] + params.get('customer_uid'),
                headers={'Authorization': access_token},
                json=data,
                timeout=5
            )
            return issue_billing_response.json()
    except Exception as e:
        raise e


@transaction.atomic(using='default')
@sync_to_async
@subscription_router.post('/payment')
def request_payment_subscription(request, payload: RequestPaymentSubscriptionsSchema):
    try:
        with transaction.atomic():
            token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
            token_response_json = token_response.json()
            if int(token_response_json['code']) == 0:
                access_token = token_response_json['response'].get('access_token')
                request_payment_response = requests.post(
                    url=REQUEST_PAYMENT['url'],
                    headers={'Authorization': access_token},
                    json=payload.json(),
                    timeout=5
                )
                if int(request_payment_response.json()['code']) == 0:  # 요청이 성공 했을 경우
                    # DB에 저장 한다.
                    Subscriptions.objects.create(
                        owner=request.auth,
                        merchant_uid=payload.dict()['merchant_uid'],
                        customer_uid=payload.dict()['customer_uid'],
                    )
                return request_payment_response.json()
            else:
                return token_response_json
    except Exception as e:
        raise e


@transaction.atomic(using='default')
@sync_to_async
@subscription_router.post('/payment/schedule')
def request_payment_schedule_subscription(request, payload: RequestPaymentSubscriptionsScheduleSchema):
    schedules = payload.dict()['schedules']
    try:
        with transaction.atomic():
            token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
            token_response_json = token_response.json()
            if int(token_response_json['code']) == 0:
                access_token = token_response_json['response'].get('access_token')
                request_payment_schedule_response = requests.post(
                    url='https://api.iamport.kr/subscribe/payments/schedule',
                    headers={'Authorization': access_token},
                    json=payload.json(),
                    timeout=5
                )

                return request_payment_schedule_response.json()
            else:
                return token_response_json
    except Exception as e:
        raise e


@sync_to_async
@subscription_router.get('/iamport_callback/schedule')
def iamport_callback(request, imp_uid: str, merchant_uid: str):
    try:
        with transaction.atomic():
            token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
            token_response_json = token_response.json()
            if int(token_response_json['code']) == 0:
                access_token = token_response_json['response'].get('access_token')
                # imp_uid 로 아임포트 서버에서 결제 정보 조회
                payment_response = requests.post(
                    url='https://api.iamport.kr/payments/' + imp_uid,
                    headers={'Authorization': access_token}
                )
                payment_response_json = payment_response.json()
                if int(payment_response_json['code']) == 0 and payment_response_json['data']:
                    status = payment_response_json['data']['response']['status']
                    if status == 'paid':
                        # DB에 저장하기.
                        Subscriptions.objects.update_or_create(
                            owner=request.auth,
                            merchant_uid=merchant_uid,
                            defaults={
                                'imp_uid': imp_uid,
                                'merchant_uid': merchant_uid,
                                'response_raw': payment_response_json
                            })
                return payment_response_json
            else:
                return token_response_json
    except Exception as e:
        raise e