import os
from typing import List, Optional

from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import transaction
from django.db.models import Prefetch

from ninja import Router, File
from ninja.files import UploadedFile
from ninja.responses import Response

from placement.constant import PlacementType
from placement.models import Placement, PlacementImage
from placement.schema import PlacementListSchema, PlacementInsertSchema, PlacementModifySchema
from util.default import ResponseDefaultHeader
from util.file import delete_files
from util.params import prepare_for_query

router = Router()


@router.get("/",
            description="플레이스 리스트 가져오기",
            tags=["place"],
            response={200: List[PlacementListSchema]},
            auth=None
            )
def get_placement_list_by_type(request, placement_type: Optional[PlacementType] = None, id: Optional[int] = None):
    params = prepare_for_query(request)
    queryset = Placement.objects.filter(**params).prefetch_related(
        Prefetch('placementimage_set', to_attr='placement_image'),
    ).all()
    return queryset


@transaction.atomic(using='default')
@router.post("/",
             description="플레이스 생성 및 수정, # operation_start,operation_end hh:mm 형식으로 보내주세요 다른 형식도 되긴할듯",
             tags=["place"], response=ResponseDefaultHeader.Schema)
def create_placement(request, payload: PlacementInsertSchema, file: UploadedFile = None):
    try:
        with transaction.atomic():
            if len(Placement.objects.filter(**payload, **file)) == 0:
                place = Placement.objects.create(**payload.dict())
                PlacementImage.objects.create(place=Placement.objects.get(id=place.id), **file)
            else:  # modify
                place = get_object_or_404(Placement, id=id)
                if len(PlacementImage.objects.filter(place=place) == 0):  # 갖고있는 이미지가 없을 떄
                    PlacementImage.objects.create(place=place, **file)
                else:
                    delete_files([place.placementimage_set.all()[0].file.name])
                    if file is not None:
                        PlacementImage.objects.filter(place=place).update(**file)
    except Exception as e:
        raise Exception(e)
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="플레이스 생성/수정이 성공적으로 되었습니다."
    )


# @transaction.atomic(using='default')
# @router.put("/", description="플레이스 수정", tags=["place"])
# def modify_placement(request, payload: PlacementModifySchema, id: int):
#     # , file: UploadedFile = File(...)):
#     # queryset = get_object_or_404(Placement, id=id)
#     try:
#         Placement.objects.filter(id=id).update(**payload.dict())
#         # queryset.placementimage_set.update(**file)
#     except Exception as e:
#         raise Exception(e)
#     return ResponseDefaultHeader(
#         code=Response.status_code,
#         message="플레이스 수정이 성공적으로 되었습니다."
#     )


@router.delete("/", description="플레이스 삭제", tags=["place"])
def delete_placement(request, id: int):
    queryset = get_object_or_404(Placement, id=id).delete()
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="플레이스 삭제가 성공적으로 되었습니다.",
        data=queryset.id
    )
