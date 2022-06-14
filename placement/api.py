from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.files import UploadedFile

from conf.custom_exception import UserNotAccessDeniedException
from placement.models import Placement
from placement.schema import PlacementListSchema, PlacementInsertSchema
from util.permission import is_admin

router = Router()


@router.get("/",
            description="플레이스 리스트 가져오기",
            response={200: List[PlacementListSchema]},
            auth=None,
            )
def get_placement_list(request):
    queryset = Placement.objects.get_queryset()
    return queryset


@router.get("/{remote_pk}",
            description="플레이스 리스트 가져오기",
            response={200: List[PlacementListSchema]},
            auth=None
            )
def get_placement_list_by_pk(request, remote_pk: int):
    queryset = Placement.objects.get_queryset(remote_pk=remote_pk)
    return queryset


@router.delete("/", description="플레이스 삭제")
def delete_placement(request, id: int):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    queryset = get_object_or_404(Placement, id=id).soft_delete()
    return queryset


@transaction.atomic(using='default')
@router.post("/",
             description="플레이스 생성")
def update_or_create_placement(request, payload: PlacementInsertSchema, id: int = None, file: UploadedFile = None):
    if not is_admin(request.auth):
        raise UserNotAccessDeniedException
    try:
        with transaction.atomic():
            params = payload.dict()
            params['image'] = file
            Placement.objects.update_or_create(id=id, defaults=params)
    except Exception as e:
        raise e
