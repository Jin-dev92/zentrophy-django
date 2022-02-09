from typing import List, Optional

from ninja import Router, File
from ninja.files import UploadedFile
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction

from member.models import Member
from order.models import Order, ExtraSubside, NecessaryDocumentFile
from order.schema import OrderListSchema, OrderCreateSchema, OrderModifySchema

router = Router()


@router.get("/", description="전체 주문 조회, id param 넣으면 id로 조회", response={200: List[OrderListSchema]})
def get_list_order(request, id: Optional[int] = None):
    params = dict()
    if id is not None:
        params['id'] = id
    queryset = Order.objects.select_related('owner').prefetch_related('extra_subside', 'order_files') \
        .filter(**params).all()
    return queryset


@router.post("/", description="주문 생성")
@transaction.atomic(using='default')
def create_order(request, payload: OrderCreateSchema, files: List[UploadedFile] = File(...)):
    payload_dict = payload.dict()
    extra_subsides = payload_dict['extra_subside']  # 추가 보조금 리스트
    owner = Member.objects.get(id=payload_dict['owner_id'])
    try:
        with transaction.atomic():
            is_created_order = Order.objects.create(
                owner=owner,
                payment_info=payload_dict['payment_info'],
                is_able_subside=payload_dict['is_able_subside']
            )  # 주문 생성
            is_created_order.extra_subside.add(**ExtraSubside.objects.in_bulk(id_list=extra_subsides))
            for_bulk_file_list = [NecessaryDocumentFile(file=file,
                                                        order=is_created_order) for file in files]
            NecessaryDocumentFile.objects.bulk_create(for_bulk_file_list)


    except Exception as e:
        raise Exception(e)


@router.put("/", description="주문 상태 변경")
def modify_order(request, id: int, state: int):
    return get_object_or_404(Order, id=id).order_change_state(state)


@router.delete("/", description="주문 삭제")
def delete_order(request, id: int):
    return Order.objects.filter(id=id).delete()
