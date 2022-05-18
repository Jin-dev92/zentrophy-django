from typing import List

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import AlreadyExistsException, LoginRequiredException
from order.constant import OrderState
from order.models import Order, Subside, DocumentFile, ExtraSubside, OrderedProductOptions, OrderedVehicleColor
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema

router = Router()
subside_router = Router()
file_router = Router()
upload_exceed_count = 5


@login_required
@router.get('/', response=List[OrderListSchema], description="주문 조건 검색")
def get_order_list(request):
    if str(request.user) == 'AnonymousUser':  # @todo 나중에 수정
        raise LoginRequiredException
    if request.user.is_staff:
        target = Order.objects.get_queryset()
    else:
        target = Order.objects.get_queryset(owner=request.user)
    queryset = target.prefetch_related(
        'extra_subside',
        'ordered_product_options',
        'ordered_vehicle_color',
        Prefetch('documentfile_set', to_attr="files")).select_related('owner')
    return queryset


@login_required
@router.get('/{id}', description="주문 id로 검색", response=List[OrderListSchema])
def get_order_list_by_id(request, id: int):
    queryset = Order.objects.get_queryset(id=id).select_related('owner').prefetch_related(
        'extra_subside',
        'ordered_product_options',
        'ordered_vehicle_color',
        Prefetch('documentfile_set', to_attr="files"))
    return queryset


@login_required
@router.post('/', description="주문 생성")
def create_order(request, payload: OrderCreateSchema):
    params = payload.dict()
    order_params = {k: v for k, v in params.items() if
                    k not in {'ordered_product_options', 'ordered_vehicle_color', 'extra_subside'}}
    order_params['owner'] = request.user
    order_queryset = Order.objects.create(**order_params)
    if params.get('extra_subside') and len(params.get('extra_subside')) > 0:
        order_queryset.extra_subside.add(
            *ExtraSubside.objects.in_bulk(id_list=params.get('extra_subside')))  # manytomany field
    if params['ordered_product_options'] and len(params['ordered_product_options']) > 0:
        order_queryset.ordered_product_options.add(
            *OrderedProductOptions.objects.bulk_create(
                objs=[
                    OrderedProductOptions(**ordered_po) for ordered_po in
                    params['ordered_product_options']]
            )
        )
    if params['ordered_vehicle_color'] and len(params['ordered_vehicle_color']) > 0 and params['ordered_vehicle_color']:
        order_queryset.ordered_vehicle_color.add(
            *OrderedVehicleColor.objects.bulk_create(
                objs=[OrderedVehicleColor(**ordered_vc) for ordered_vc in params['ordered_vehicle_color']])
        )


@login_required
@router.put('/', description="주문 상태 수정, OrderListSchema - state 주석 참조")
def change_order_state(request, id: int, state: OrderState):
    target = get_object_or_404(Order, id=id)
    target.state = state
    target.save(update_fields=['state'])


@login_required
@router.put('/', description="주문 내역 수정")
def modify_order(request, id: int):
    pass


@login_required
@router.delete('/', description="주문 삭제")
def delete_order_list_by_id(request, id: int):
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
    order = get_object_or_404(Order, id=order_id)
    queryset = DocumentFile.objects.bulk_create(
        objs=[DocumentFile(order=order, file=file) for file in files], batch_size=upload_exceed_count)


@login_required
@file_router.delete('/', description="계획서 및 보조금 신청서 삭제")
def delete_files(request, id: int):
    queryset = get_object_or_404(DocumentFile, id=id).delete()
    return queryset
