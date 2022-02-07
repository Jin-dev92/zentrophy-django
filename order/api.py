from typing import List

from ninja import Router, File
from ninja.files import UploadedFile
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction

from member.models import Member
from order.models import Order, ExtraSubside, NecessaryDocumentFile
from order.schema import OrderListSchema, OrderCreateSchema
from product.models import Vehicle, Product

router = Router()


@router.get("/", description="전체 주문 조회", response={200: List[OrderListSchema]})
def get_list_order(request):
    return Order.objects.all()


@router.get("/${id}", description="pk로 특정 주문 조회", response={200: OrderListSchema})
def get_list_order_by_id(request, id: int):
    get_object_or_404(Order, id=id).delete()


@router.post("/", description="주문 생성")
@transaction.atomic(using='default')
def create_order(request, payload: OrderCreateSchema, files: List[UploadedFile] = File(...)):
    payload_dict = payload.dict()
    owner = payload_dict['owner']
    extra_subsides = payload_dict['extra_subside']  # 추가 보조금 리스트
    vehicles = payload_dict['vehicle']  # 구매한 탈것 리스트
    products = payload_dict['product']  # 구매한 product_id 리스트
    try:
        with transaction.atomic():
            is_created_order = Order.objects.create(
                owner=Member.objects.get(id=owner),
                amount=payload_dict['amount']
            )  # 주문 생성
            is_created_order.extra_subside.add(ExtraSubside.objects.in_bulk(id_list=list(extra_subsides)))
            is_created_order.vehicle.add(Vehicle.objects.in_bulk(id_list=list(vehicles)))
            is_created_order.product.add(Product.objects.in_bulk(id_list=list(products)))
        for file in files:
            NecessaryDocumentFile.objects.create(
                file=file,
                order=is_created_order.id
            )

    except Exception as e:
        raise e


@router.put("/", description="주문 수정")
def modify_order(request, payload: OrderCreateSchema, id: int):
    return None


@router.delete("/", description="주문 삭제")
def delete_order(request, payload: OrderCreateSchema, id: int):
    return None
