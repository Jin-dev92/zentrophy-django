from typing import List, Optional
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from placement.constant import PlacementType
from placement.models import Placement, PlacementImage
from placement.schema import PlacementListSchema, PlacementInsertSchema
from util.file import delete_file
from util.params import prepare_for_query

from sorl.thumbnail import delete

router = Router()


@router.get("/",
            description="플레이스 리스트 가져오기",
            tags=["place"],
            response={200: List[PlacementListSchema]},
            auth=None
            )
def get_placement_list_by_type(request, placement_type: PlacementType = PlacementType.SERVICE, id: Optional[int] = None):
    params = prepare_for_query(request)
    queryset = Placement.objects.get_queryset(**params).prefetch_related(
        Prefetch('placementimage_set', to_attr='placement_image'),
    ).all()
    return queryset


@router.get('/{id}', response={200: List[PlacementListSchema]})
def get_placement_by_id(request, id: int):
    queryset = Placement.objects.get_queryset(id=id).prefetch_related(
        Prefetch('placementimage_set', to_attr='placement_image'),
    ).all()
    return queryset


@transaction.atomic(using='default')
@router.post("/", description="플레이스 생성, # operation_start,operation_end hh:mm 형식으로 보내주세요 다른 형식도 되긴할듯")
def create_placement(request, payload: PlacementInsertSchema, file: UploadedFile = None):
    try:
        with transaction.atomic():
            if len(Placement.objects.get_queryset(**payload.dict())) == 0:
                place = Placement.objects.create(**payload.dict())
                if file:
                    PlacementImage.objects.create(place=place, file=file)
    except Exception as e:
        raise Exception(e)
    return True


@transaction.atomic(using='default')
@router.post('/{id}', description="플레이스 정보 수정")
def modify_placement_by_id(request, payload: PlacementInsertSchema, id: int, file: UploadedFile = None):
    place = get_object_or_404(Placement, id=id, deleted_at__isnull=True)
    # for image in place.placementimage_set.all():
    #     print(image.file)
    # return
    try:
        with transaction.atomic():
            PlacementImage.objects.filter(place=place).delete()
            for image in place.placementimage_set.all():
                delete_file(image.file)
            Placement.objects.get_queryset(id=id).update(**payload.dict())
            if file:
                PlacementImage.objects.create(place=place, file=file)
    except Exception as e:
        raise e

    # return True


@router.delete("/", description="플레이스 삭제")
def delete_placement(request, id: int):
    queryset = get_object_or_404(Placement, id=id).soft_delete()
    return queryset
