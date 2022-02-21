from typing import List, Optional

from ninja import Router
from ninja.files import UploadedFile
from ninja.responses import Response

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch

from member.models import Member
from order.constant import OrderState
from order.models import Order, ExtraSubside, NecessaryDocumentFile
from order.schema import OrderListSchema, OrderCreateSchema
from util.default import ResponseDefaultHeader
from util.params import prepare_for_query

router = Router()


@router.get("/", description="전체 주문 조회, id param 넣으면 id로 조회", response={200: List[OrderListSchema]})
def get_list_order(request, id: Optional[int] = None):
    params = prepare_for_query(request)
    queryset = Order.objects.select_related('owner').prefetch_related(
        Prefetch('extra_subside', to_attr="extra_subside"),
        Prefetch('order_files', to_attr="files")) \
        .filter(**params).all()
    return queryset


@router.post("/", description="주문 생성/수정, payment_info : 결제 후 return 되는 값을 넣어야함.", response=ResponseDefaultHeader.Schema)
@transaction.atomic(using='default')
def create_order(request, payload: OrderCreateSchema, files: List[UploadedFile] = None):
    payload_dict = payload.dict()
    extra_subsides_id: list = payload_dict['extra_subside_id']  # 추가 보조금 리스트
    owner = get_object_or_404(Member, id=payload_dict['owner_id'])
    try:
        with transaction.atomic():
            is_created_order = Order.objects.update_or_create(
                owner=owner,
                payment_info=payload_dict['payment_info'],
                is_able_subside=payload_dict['is_able_subside']
            )  # 주문 생성
            is_created_order.extra_subside.add(*ExtraSubside.objects.in_bulk(id_list=extra_subsides_id))
            for_bulk_file_list = [NecessaryDocumentFile(file=file,
                                                        order=is_created_order) for file in files]
            NecessaryDocumentFile.objects.bulk_create(for_bulk_file_list)


    except Exception as e:
        raise Exception(e)

    return ResponseDefaultHeader(
        code=Response.status_code,
        message="해당 주문이 생성 되었습니다.",
    )


@router.put("/", description="주문 상태 변경", response=ResponseDefaultHeader.Schema)
def modify_order(request, id: int, state: OrderState):
    qs = get_object_or_404(Order, id=id).order_change_state(state)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="해당 주문 상태가 변경 되었습니다.",
        data=qs
    )


@router.delete("/", description="주문 삭제", response=ResponseDefaultHeader.Schema)
def delete_order(request, id: int):
    qs = get_object_or_404(Order, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="해당 주문이 삭제되었습니다.",
        data=qs
    )
