from typing import List

from django.shortcuts import get_list_or_404, get_object_or_404

from ninja import Router
from placement.constant import PlacementType
from placement.models import Placement
from placement.schema import PlacementListSchema, PlacementInsertSchema, PlacementModifySchema

router = Router()


@router.get("/{placement_type}",
            description="타입으로 플레이스 리스트 가져오기",
            tags=["place"],
            response={200: List[PlacementListSchema]}
            )
def get_placement_list_by_type(request, placement_type: PlacementType):
    return get_list_or_404(Placement, placement_type=placement_type)


@router.get("/", description="플레이스 pk로 해당 플레이스 정보 가져오기", response={200: List[PlacementListSchema]},
            tags=["place"]
            )
def get_placement_list_by_id(request, id: int):
    return get_list_or_404(Placement, id=id)


@router.post("/", description="플레이스 생성, # operation_start,operation_end hh:mm 형식으로 보내주세요 다른 형식도 되긴할듯",
             tags=["place"])
def create_placement(request, payload: PlacementInsertSchema):
    return Placement.objects.create(**payload.dict())


@router.put("/", description="플레이스 수정", tags=["place"])
def modify_placement(request, payload: PlacementModifySchema, id: int):
    qs = get_object_or_404(Placement, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@router.delete("/", description="플레이스 삭제", tags=["place"])
def delete_placement(request, id: int):
    return get_object_or_404(Placement, id=id).delete()
