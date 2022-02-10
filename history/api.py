from typing import List

from ninja import UploadedFile, File, Router

from history.models import AfterService
from history.schema import HistoryListSchema
# from util.number import generate_register_number
from util.number import generate_random_number

history_router = Router()
refund_router = Router()
after_service_router = Router()


@history_router.post("/", description="a/s 내역 생성")
def create_after_service_history(request):
    registration_number = generate_random_number()
    return registration_number
    # return AfterService.objects.create(registration_number=registration_number)
