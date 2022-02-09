from typing import List, Optional

from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from ninja import Router, File
from ninja.files import UploadedFile
from placement.constant import PlacementType
from placement.models import Placement, PlacementImage
from placement.schema import PlacementListSchema, PlacementInsertSchema, PlacementModifySchema

router = Router()


@router.get("/",
            description="플레이스 리스트 가져오기",
            tags=["place"],
            response={200: List[PlacementListSchema]}
            )
def get_placement_list_by_type(request, placement_type: Optional[PlacementType] = None, id: Optional[int] = None):
    param = {}
    if placement_type is not None:
        param['placement_type'] = placement_type
    if id is not None:
        param['id'] = id
    return Placement.objects.filter(**param).prefetch_related('placementimage_set').all()


@transaction.atomic(using='default')
@router.post("/", description="플레이스 생성, # operation_start,operation_end hh:mm 형식으로 보내주세요 다른 형식도 되긴할듯",
             tags=["place"])
def create_placement(request, payload: PlacementInsertSchema, file: UploadedFile = File(...)):
    try:
        with transaction.atomic():
            place = Placement.objects.create(**payload.dict())
            PlacementImage.objects.create(
                place=Placement.objects.get(id=place.id),
                file=file
            )
    except Exception as e:
        raise Exception(e)


@transaction.atomic(using='default')
@router.put("/", description="플레이스 수정", tags=["place"])
def modify_placement(request, payload: PlacementModifySchema, id: int, files: List[UploadedFile] = File(...)):
    qs = get_object_or_404(Placement, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@router.delete("/", description="플레이스 삭제", tags=["place"])
def delete_placement(request, id: int):
    return get_object_or_404(Placement, id=id).delete()
