from typing import List, Optional

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
# from django.contrib.auth.decorators import permission_required
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import LoginRequiredException, AlreadyExistsException
from member.models import PaymentMethod
from order.constant import OrderState
from order.models import Order, Subside, NecessaryDocumentFile, OrderDetail, ExtraSubside
from order.schema import OrderListSchema, OrderCreateSchema, SubsideListSchema, SubsideInsertSchema
from product.models import Product, Vehicle
# from util.file import delete_files
from util.params import prepare_for_query
from util.permission import has_permission

router = Router()
subside_router = Router()


@login_required
@transaction.atomic(using='default')
@router.post("/", description="주문 생성")
def create_order(request, payload: OrderCreateSchema, files: List[UploadedFile] = None):
    # if not has_permission or str(request.user) == 'AnonymousUser':
    #     raise LoginRequiredException
    payload_dict = payload.dict()
    extra_subsides_id: list = payload_dict['extra_subside_id']  # 추가 보조금 리스트 pk
    order_detail: dict = payload_dict['order_detail']
    try:
        with transaction.atomic():
            is_created_order = Order.objects.update_or_create(
                owner=request.user,
                payment_type=payload_dict['payment_type'],
                payment_method=PaymentMethod.objects.get(id=payload_dict['payment_method']),
                payment_info=payload_dict['payment_info'],
                is_able_subside=payload_dict['is_able_subside']
            )  # 주문 생성
        for detail in order_detail:
            OrderDetail.objects.create(
                order=is_created_order[0],
                product_options=Product.objects.get(id=detail['product_options']),
                vehicle_color=Vehicle.objects.get(id=detail['w']),
                amount=detail['amount'],
            )

            for_bulk_file_list = [NecessaryDocumentFile(file=file,
                                                        order=is_created_order[0]) for file in files]
            if is_created_order[1]:  # create
                is_created_order[0].extra_subside.add(*Subside.objects.in_bulk(id_list=extra_subsides_id))
                NecessaryDocumentFile.objects.bulk_create(for_bulk_file_list)
                is_created_order[0].sales_products()
            else:  # update
                is_created_order[0].extra_subside.add(**Subside.objects.in_bulk(id_list=extra_subsides_id))
                # delete_files([file.file.name for file in for_bulk_file_list])
            is_created_order[0].save()
    except Exception as e:
        raise Exception(e)

    return True


@router.get("/", description="전체 주문 조회, id param 넣으면 id로 조회",
            response={200: List[OrderListSchema]},
            auth=None
            )
def get_list_order(request, id: Optional[int] = None):
    params = prepare_for_query(request)
    queryset = Order.objects.get_queryset(**params).select_related('owner').prefetch_related(
        # Prefetch('extra_subside', to_attr="extra_subside"),
        Prefetch('necessarydocumentfile_set', to_attr="files"))
    return queryset


@router.get('/{id}', description="주문 get by id", response={200: List[OrderListSchema]})
def get_order_by_id(request, id: int):
    queryset = Order.objects.get_queryset(id=id).select_related('owner').prefetch_related(
        Prefetch('necessarydocumentfile_set', to_attr="files"))
    return queryset


@router.put("/", description="주문 상태 변경")
def modify_order(request, id: int, state: OrderState):
    queryset = get_object_or_404(Order, id=id).order_change_state(state)
    return queryset


@router.delete("/", description="주문 삭제")
def delete_order(request, id: int):
    queryset = get_object_or_404(Order, id=id).soft_delete()
    return queryset


@subside_router.get('/', response=List[SubsideListSchema])
def get_list_subside(request):
    queryset = Subside.objects.get_queryset().prefetch_related(
        Prefetch('extrasubside_set', to_attr="extra")
    )
    return queryset


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


# @subside_router.put('/')
# def modify_subside_amount(request, amount: int):
#     obj = Subside.objects.all().first()
#     obj.amount = amount
#     obj.save(update_fields=['amount'])


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

# @subside_router.delete('/')
# def delete_subside(id: int):
#     queryset = get_object_or_404(Subside, id=id).soft_delete()
#     return queryset
