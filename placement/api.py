from typing import List
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from placement.models import Placement
from placement.schema import PlacementListSchema, PlacementInsertSchema
from util.params import prepare_for_query

router = Router()


@router.get("/",
            description="플레이스 리스트 가져오기",
            response={200: List[PlacementListSchema]},
            auth=None
            )
def get_placement_list_by_type(request, remote_pk: int = None):
    params = prepare_for_query(request)
    queryset = Placement.objects.get_queryset(**params)
    return queryset


@router.get('/{id}', response={200: List[PlacementListSchema]})
def get_placement_by_id(request, id: int):
    queryset = Placement.objects.get_queryset(id=id)
    return queryset


@transaction.atomic(using='default')
@router.post("/",
             description="플레이스 생성")
def create_placement(request, payload: PlacementInsertSchema, id: int = None, file: UploadedFile = None):
    try:
        with transaction.atomic():
            params = payload.dict()
            params['image'] = file
            Placement.objects.update_or_create(id=id, defaults=params)
    except Exception as e:
        raise e


@router.delete("/", description="플레이스 삭제")
def delete_placement(request, id: int):
    queryset = get_object_or_404(Placement, id=id).soft_delete()
    return queryset
