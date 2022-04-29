from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router

from conf.custom_exception import DataBaseORMException
from post.models import FAQ, Notice, FAQCategory
from post.schema import FAQInsertSchema, FAQListSchema, NoticeListSchema, NoticeInsertSchema, FAQCategorySchema
from util.params import prepare_for_query

faq_router = Router()
notice_router = Router()
faq_category_router = Router()


@faq_router.get('/', description="FAQ 목록", response=List[FAQListSchema], auth=None)
def get_faq_list(request, category: int = None):
    params = prepare_for_query(request)
    return FAQ.objects.get_queryset(**params)


@faq_router.get('/{id}', description="FAQ get by id", response=List[FAQListSchema], auth=None)
def get_faq_list(request, id: int):
    return FAQ.objects.get_queryset(id=id)


@transaction.atomic(using='default')
@faq_router.post("/", description="FAQ 생성 / 수정")
def create_faq(request, payload: FAQInsertSchema, id: int = None):
    try:
        with transaction.atomic():
            obj = FAQ.objects.update_or_create(id=id, defaults=payload.dict())

    except Exception as e:
        print(e)
        raise DataBaseORMException


@faq_router.delete("/", description="FAQ 삭제")
def delete_faq(request, id: int):
    queryset = get_object_or_404(FAQ, id=id).soft_delete()
    # return ResponseDefaultHeader(
    #     code=Response.status_code,
    #     message="FAQ가 삭제되었습니다",
    #     data=queryset
    # )


@notice_router.get('/', description="공지사항 리스트", response=List[NoticeListSchema], auth=None)
def get_notice_list(request, id: int):
    params = prepare_for_query(request)
    queryset = Notice.objects.get_queryset(**params).all()
    return queryset


@transaction.atomic(using='default')
@notice_router.post('/', description="공지사항 리스트 생성/수정")
def create_notice(request, payload: NoticeInsertSchema):
    try:
        with transaction.atomic():
            Notice.objects.update_or_create(**payload.dict())

    except Exception as e:
        raise DataBaseORMException

    # return ResponseDefaultHeader(
    #     code=Response.status_code,
    #     message="공지사항 생성 혹은 수정이 되었습니다."
    # )


@notice_router.delete("/", description="공지사항 삭제")
def delete_notice(request, id: int):
    queryset = get_object_or_404(Notice, id=id).soft_delete()
    # return ResponseDefaultHeader(
    #     code=Response.status_code,
    #     message="공지사항이 삭제되었습니다",
    #     data=queryset
    # )


@faq_category_router.get('/', description="FAQ 카테고리 리스트", response=List[FAQCategorySchema], auth=None)
def get_faq_category_list(request):
    return FAQCategory.objects.all()


@faq_category_router.post('/', description='FAQ 카테고리 생성')
def create_faq_category(request, category_name: str):
    queryset = FAQCategory.objects.create(category_name=category_name)


@faq_category_router.delete('/', description='FAQ 카테고리 삭제')
def delete_faq_category(request, id: int):
    queryset = get_object_or_404(FAQCategory, id=id).soft_delete()
