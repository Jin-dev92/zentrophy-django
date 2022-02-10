from typing import List
from django.shortcuts import get_object_or_404
from ninja import UploadedFile, File, Router

from history.models import AfterService
from history.schema import HistoryListSchema, AfterServiceInsertSchema
# from util.number import generate_register_number
from placement.models import Placement
from util.number import generate_random_number

history_router = Router()
refund_router = Router()
after_service_router = Router()


@history_router.post("/", description="a/s 내역 생성")
def create_after_service_history(request, payload: AfterServiceInsertSchema):
    registration_number = generate_random_number()
    # place = get_object_or_404(Placement, id=payload.dict()['place_id'])
    # return AfterService.objects.create(registration_number=registration_number, place=place)
    return registration_number
