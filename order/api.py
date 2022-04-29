from typing import List

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import AlreadyExistsException, IncorrectTotalAmountException, \
    WrongParameterException
from order.models import Order, Subside, NecessaryDocumentFile, ExtraSubside
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema
from product.models import ProductOptions, VehicleColor
from util.params import prepare_for_query

router = Router()
subside_router = Router()
file_router = Router()
upload_exceed_count = 5


@login_required
@router.get('/', response=List[OrderListSchema], description="주문 조건 검색")
def get_order_list(request):
    params = prepare_for_query(request)
    queryset = Order.objects.get_queryset(params).select_related('owner') \
        .prefetch_related('extra_subside',
                          Prefetch('necessarydocumentfile_set', to_attr="files"))
    return queryset


@login_required
@router.get('/{id}', description="주문 id로 검색", response=List[OrderListSchema])
def get_order_list_by_id(request, id: int):
    queryset = Order.objects.get_queryset(id=id).select_related('owner') \
        .prefetch_related('extra_subside',
                          Prefetch('necessarydocumentfile_set', to_attr="files"))
    return queryset


@login_required
@router.post('/', description="주문 생성 / 수정")
def update_or_create_order(request, payload: OrderCreateSchema, id: int = None):
    payload = payload.dict()
    order_params = {k: v for k, v in payload.items() if k not in {'buy_list', 'extra_subside'}}
    order_params['buy_list']: list = []
    order_params['owner'] = request.user
    buy_list: list[dict] = payload.get('buy_list')
    # 총금액 계산 -> 총 금액 validator -> True 시 json_data 생성
    total = 0
    for goods in buy_list:
        if goods.get('product_options_pk') > 0:  # goods 가 상품 일 때
            product_options = get_object_or_404(ProductOptions, id=goods.get('product_options_pk'))
            total += int(goods.get('amount')) * product_options.product.product_price
            order_params['buy_list'].append(
                {
                    'product': product_options.product.objects.values(),
                    'product_options': product_options.objects.values(),
                    'amount': int(goods.get('amount'))
                }
            )
        elif goods.get('vehicle_color_pk') > 0:  # goods 가 모터 사이클 일 때
            vehicle_color = get_object_or_404(VehicleColor, id=goods.get('vehicle_color_pk'))
            total += int(goods.get('amount')) * vehicle_color.price
            order_params['buy_list'].append(
                {
                    'vehicle': vehicle_color.vehicle.objects.values(),
                    'vehicle_color': vehicle_color.objects.values(),
                    'amount': int(goods.get('amount'))
                }
            )
        else:
            raise WrongParameterException

    print("order_params['buy_list'] :", order_params['buy_list'])
    if int(payload.get('total')) != total:
        raise IncorrectTotalAmountException
    order_queryset = Order.objects.update_or_create(id=id, defaults=order_params)
    order_queryset[0].extra_subside.add(
        ExtraSubside.objects.in_bulk(id_list=payload.get('extra_subside')))  # manytomany field


@login_required
@router.delete('/', description="주문 삭제")
def get_order_list_by_id(request, id: int):
    queryset = get_object_or_404(Order, id=id).soft_delete()
    return queryset


@login_required
@subside_router.get('/', response=List[SubsideListSchema])
def get_list_subside(request):
    queryset = Subside.objects.get_queryset().prefetch_related(
        Prefetch('extrasubside_set', to_attr="extra")
    )
    return queryset


@login_required
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
@subside_router.put('/')
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
    # order = get_object_or_404(Order, id=order_id)
    queryset = NecessaryDocumentFile.objects.bulk_create(
        objs=[NecessaryDocumentFile(order_id=order_id, file=file) for file in files], batch_size=upload_exceed_count)
    return queryset


@login_required
@file_router.delete('/', description="계획서 및 보조금 신청서 삭제")
def delete_files(request, id: int):
    queryset = get_object_or_404(NecessaryDocumentFile, id=id).delete()
    return queryset
