from typing import List

from django.db import transaction
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from ninja import Router

from conf.custom_exception import DataBaseORMException
from post.models import FAQ, Notice, FAQCategory
from post.schema import FAQInsertSchema, FAQListSchema, NoticeListSchema, NoticeInsertSchema, FAQCategorySchema
from util.decorator import admin_permission
from util.exception.constant import DB_UNIQUE_CONSTRAINT
from util.params import prepare_for_query

faq_router = Router()
notice_router = Router()
faq_category_router = Router()


@faq_router.get('/', description="FAQ 목록", response=List[FAQListSchema], auth=None)
def get_faq_list(request, category: int = None):
    params = prepare_for_query(request)
    return FAQ.objects.get_queryset(**params)


@faq_router.get('/{id}', description="FAQ get by id", response=List[FAQListSchema], auth=None)
def get_faq_list_by_id(request, id: int):
    return FAQ.objects.get_queryset(id=id)


@transaction.atomic(using='default')
@faq_router.post("/", description="FAQ 생성 / 수정")
@admin_permission
def update_or_create_faq(request, payload: FAQInsertSchema, id: int = None):
    params = payload.dict()
    try:
        with transaction.atomic():
            obj = FAQ.objects.update_or_create(id=id, defaults=params)

    except Exception as e:
        raise e


@faq_router.delete("/", description="FAQ 삭제")
@admin_permission
def delete_faq(request, id: int):
    queryset = get_object_or_404(FAQ, id=id).soft_delete()


@notice_router.get('/', description="공지사항 리스트", response=List[NoticeListSchema], auth=None)
def get_notice_list(request, id: int = None):
    params = prepare_for_query(request)
    queryset = Notice.objects.get_queryset(**params).all()
    return queryset


@transaction.atomic(using='default')
@notice_router.post('/', description="공지사항 리스트 생성/수정")
@admin_permission
def create_notice(request, payload: NoticeInsertSchema, id: int = None):
    try:
        with transaction.atomic():
            if id and id > 0:
                get_object_or_404(Notice, id=id)
            Notice.objects.update_or_create(id=id, defaults=payload.dict())

    except Exception as e:
        raise DataBaseORMException


@notice_router.delete("/", description="공지사항 삭제")
@admin_permission
def delete_notice(request, id: int):
    queryset = get_object_or_404(Notice, id=id).soft_delete()


@faq_category_router.get('/', description="FAQ 카테고리 리스트", response=List[FAQCategorySchema], auth=None)
def get_faq_category_list(request):
    return FAQCategory.objects.all()


@faq_category_router.post('/', description='FAQ 카테고리 생성 / 수정')
@admin_permission
def update_or_create_faq_category(request, category_name: str):
    try:
        queryset = FAQCategory.objects.create(category_name=category_name)
    except IntegrityError:
        raise IntegrityError(DB_UNIQUE_CONSTRAINT['desc'])


@faq_category_router.delete('/', description='FAQ 카테고리 삭제')
@admin_permission
def delete_faq_category(request, id: int):
    queryset = get_object_or_404(FAQCategory, id=id).soft_delete()
