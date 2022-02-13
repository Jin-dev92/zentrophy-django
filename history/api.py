# from datetime import datetime, date
from datetime import date
from datetime import datetime
from typing import List
from django.shortcuts import get_object_or_404, get_list_or_404
from ninja import UploadedFile, File, Router

from history.constant import AfterServiceStatus
from history.models import AfterService
from history.schema import HistoryListSchema, AfterServiceInsertSchema, AfterServiceListSchema
from placement.models import Placement
from util.number import generate_random_number

history_router = Router()
refund_router = Router()
after_service_router = Router()


@after_service_router.get("/", description="a/s 내역 보기")
def get_after_service_list(request, id: int = None, status: AfterServiceStatus = None, start_date: date = None,
                           end_date: date = None):
    params = dict()
    if id is not None:
        params['id'] = id
    if status is not None:
        params['status'] = status
    if start_date is not None:
        params['is_created__gte'] = datetime.combine(start_date, datetime.min.time())  # tz-zone 시간으로 변경
    else:
        params['is_created__gte'] = datetime.combine(0, datetime.min.time())
    if end_date is not None:
        params['is_created__lte'] = datetime.combine(end_date, datetime.min.time())
    else:
        params['is_created__lte'] = datetime.now()
    qs = AfterService.objects.filter(**params).prefetch_related('place__afterservice_set',
                                                                'vehicle__owner__memberownedvehicles_set').all()
    print(qs.values())


@after_service_router.post("/", description="a/s 내역 생성")
def create_after_service_history(request, payload: AfterServiceInsertSchema):
    place = get_object_or_404(Placement, id=payload.dict()['place_id'])
    member = get_object_or_404(Placement, id=payload.dict()['member_id'])
    return AfterService.objects.create(
        place=place,
        owner=member,
        registration_number=generate_random_number(),
    )


@after_service_router.put("/", description="a/s 상태수정")
def change_after_service_status(request, id: int, status: AfterServiceStatus):
    return AfterService.objects.filter(id=id).update(status=status)
