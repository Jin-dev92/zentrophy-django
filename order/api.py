from typing import List

from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import F
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile
import requests

from conf.custom_exception import AlreadyExistsException, LoginRequiredException, WrongParameterException, \
    NotEnoughStockException, UserNotAccessDeniedException
from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, REQUEST_PAYMENT
from order.constant import OrderState
from order.models import Order, Subside, DocumentFile, ExtraSubside, OrderedProductOptions, OrderedVehicleColor, \
    OrderLocationInfo, CustomerInfo, DocumentFormat, Subscriptions
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema, \
    DocumentFormatListSchema, SubscriptionsCreateSchema, RequestPaymentSubscriptionsSchema, \
    RequestPaymentSubscriptionsScheduleSchema
from product.models import ProductOptions, VehicleColor
from util.number import check_invalid_product_params


router = Router()
subside_router = Router()
file_router = Router()
subscription_router = Router()

upload_exceed_count = 5


@login_required
@router.get('/', response=List[OrderListSchema], description="주문 검색")
def get_order_list(request):
    if str(request.auth) == 'AnonymousUser':  # @todo 디버그 모드 on 일때 에러 방지.
        raise LoginRequiredException
    if request.auth.is_staff:
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


@login_required
@router.get('/{id}', description="주문 id로 검색", response=List[OrderListSchema])
def get_order_list_by_id(request, id: int):
    if request.auth.is_staff:
        target = Order.objects.get_queryset()
    else:
        target = Order.objects.get_queryset(id=id, owner=request.auth)

    queryset = target.prefetch_related(
        'customer_info',
        'order_location_info',
        Prefetch(lookup='orderedproductoptions_set',
                 queryset=OrderedProductOptions.objects.select_related('product_options'),
                 to_attr="ordered_product_options"),
        Prefetch(lookup='orderedvehiclecolor_set',
                 queryset=OrderedVehicleColor.objects.select_related('vehicle_color')
                 .prefetch_related(Prefetch('vehicle_color__vehicleimage_set', to_attr='vehicle_image')),
                 to_attr="ordered_vehicle_color"),
        Prefetch(lookup='documentfile_set', to_attr="files"),
    )
    return queryset


@login_required
@transaction.atomic(using='default')
@router.post('/', description="주문 생성")
def create_order(request, payload: OrderCreateSchema):
    if str(request.auth) == 'AnonymousUser':
        raise LoginRequiredException
    try:
        with transaction.atomic():
            params = payload.dict()
            order_params = {k: v for k, v in params.items() if
                            k not in {'ordered_product_options', 'ordered_vehicle_color', 'extra_subside',
                                      'customer_info',
                                      'order_location_info'}}
            order_params['owner'] = request.auth
            order_location_info_params = params['order_location_info']
            customer_info_params = params['customer_info']
            customer_object = CustomerInfo.objects.create(**customer_info_params)
            location_object = OrderLocationInfo.objects.create(**order_location_info_params)
            order_queryset = Order.objects.create(**order_params, customer_info=customer_object, order_location_info=location_object)  # 주문 생성
            if params.get('extra_subside') and len(params.get('extra_subside')) > 0:
                order_queryset.extra_subside.add(
                    *ExtraSubside.objects.in_bulk(id_list=params.get('extra_subside')))  # manytomany field
            if params['ordered_product_options'] and len(params['ordered_product_options']) > 0:
                if not check_invalid_product_params(params['ordered_product_options']):     # 파라미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                po_list = OrderedProductOptions.objects.bulk_create(
                        objs=[
                            OrderedProductOptions(**ordered_po,
                                                  order=order_queryset)
                            for ordered_po in params['ordered_product_options']]
                    )
                for index, po in enumerate(params['ordered_product_options']):    # 주문 생성 시 판매량, 재고량 조절
                    po_target = get_object_or_404(ProductOptions, id=po.get('product_options_id'))
                    if po.get('amount') > po_target.stock_count:
                        raise NotEnoughStockException
                    po_target.sale_count = po_target.sale_count + po.get('amount')
                    po_target.stock_count = po_target.stock_count - po.get('amount')
                    po_target.save(update_fields=['sale_count', 'stock_count'])

            elif params['ordered_vehicle_color'] and len(params['ordered_vehicle_color']) > 0:
                if not check_invalid_product_params(params['ordered_vehicle_color']): # 파라미터 잘못 보냈는지 체크 (수량 0 이거나 id 가 0 or 음수일 때)
                    raise WrongParameterException
                vc_list = OrderedVehicleColor.objects.bulk_create(
                    objs=[OrderedVehicleColor(**ordered_vc, order=order_queryset) for ordered_vc in params['ordered_vehicle_color']])
                for index, vc in enumerate(params['ordered_vehicle_color']):  # 주문 생성시 판매량, 재고량 조절
                    vc_target = get_object_or_404(VehicleColor, id=vc.get('vehicle_color_id'))
                    if vc.get('amount') > vc_target.stock_count:
                        raise NotEnoughStockException
                    vc_target.sale_count = vc_target.sale_count + vc.get('amount')
                    vc_target.stock_count = vc_target.stock_count - vc.get('amount')
                    vc_target.save(update_fields=['sale_count', 'stock_count'])
            else:
                raise WrongParameterException

    except Exception as e:
        raise e


@login_required
@router.put('/', description="주문 상태 수정, OrderListSchema - state 주석 참조")
def change_order_state(request, id: int, state: OrderState):
    target = get_object_or_404(Order, id=id)
    target.state = state
    target.save(update_fields=['state'])


# @login_required
# @router.put('/', description="주문 내역 수정")
# def modify_order(request, id: int):
#     pass


@login_required
@router.delete('/', description="주문 삭제")
def delete_order_list_by_id(request, id: int):
    target = get_object_or_404(Order, id=id)
    queryset = target.soft_delete()


# @login_required
@subside_router.get('/', response=List[SubsideListSchema])
def get_list_subside(request):
    queryset = Subside.objects.get_queryset().prefetch_related(
        Prefetch('extrasubside_set', to_attr="extra")
    )
    return queryset


# @login_required
@transaction.atomic(using='default')
@subside_router.post('/')
def create_subside(request, payload: SubsideInsertSchema):
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


@login_required
@subside_router.put('/', description="기본 보조금 수정")
def modify_extra_subside(request, payload: SubsideInsertSchema = None):
    for extra_subside in ExtraSubside.objects.get_queryset():
        extra_subside.soft_delete()
    if payload:
        subside = Subside.objects.all().first()
        subside.amount = payload.amount
        subside.save(update_fields=['amount'])
        extra_list = [ExtraSubside(**item, subside=subside) for item in payload.dict().get('extra')]
        queryset = ExtraSubside.objects.bulk_create(objs=extra_list)
    return True


@login_required
@file_router.post('/', description="계획서 및 보조금 신청서 업로드")
def upload_files(request, order_id: int, files: List[UploadedFile]):
    order = get_object_or_404(Order, id=order_id)
    queryset = DocumentFile.objects.bulk_create(
        objs=[DocumentFile(order=order, file=file) for file in files], batch_size=upload_exceed_count)


@login_required
@file_router.delete('/', description="계획서 및 보조금 신청서 삭제")
def delete_files(request, id: int):
    queryset = get_object_or_404(DocumentFile, id=id).delete()


# @login_required
# @file_router.get('/format', description="보조금 신청서 포맷 다운 로드")
# def download_format_files(request, id: int):
#     target = get_object_or_404(DocumentFormat, id=id)
#     fs = FileSystemStorage(target.file.path)
#     response = FileResponse(fs.open(target.file.path))
#     response['Content-Disposition'] = f'attachment; filename={target.file.name}'
#     print(request)
    # return response


@login_required
@file_router.get('/format', description="보조금 신청서 포맷 리스트", response=List[DocumentFormatListSchema])
def get_format_list(request):
    queryset = DocumentFormat.objects.get_queryset()
    return queryset


@login_required
@file_router.post('/format', description="보조금 신청서 포맷 업로드")
def upload_format_files(request, file: UploadedFile):
    if not request.auth.is_staff:
        raise UserNotAccessDeniedException
    queryset = DocumentFormat.objects.create(file=file)


@login_required
@file_router.delete('/format', description="보조금 신청서 포맷 삭제")
def delete_format_files(request, id: int):
    if not request.auth.is_staff:
        raise UserNotAccessDeniedException
    target = get_object_or_404(DocumentFormat, id=id)
    queryset = target.soft_delete()


@login_required
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
            # if issue_billing_response.json()['code'] != 0:
            #     print(issue_billing_response.json())
    except Exception as e:
        raise e


@login_required
@sync_to_async
@subscription_router.post('/payment')
def request_payment_subscription(request, payload: RequestPaymentSubscriptionsSchema):
    try:
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
            return request_payment_response.json()
        else:
            return token_response_json
    except Exception as e:
        raise e


@login_required
@sync_to_async
@subscription_router.post('/payment/schedule')
def request_payment_schedule_subscription(request, payload: RequestPaymentSubscriptionsScheduleSchema):
    try:
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


@login_required
@sync_to_async
@subscription_router.get('/iamport_callback/schedule')
def iamport_callback(request, imp_uid: str, merchant_uid: str):
    try:
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
            if payment_response_json['code'] == 0 and payment_response_json['data']:
                status = payment_response_json['data']['response']['status']
                if status == 'paid':
                    # DB에 저장하기.
                    Subscriptions.objects.update_or_create(
                        imp_uid=imp_uid,
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