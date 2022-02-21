# from datetime import datetime, date, time
from datetime import time
from typing import List

from ninja import Schema
from pydantic import Field
from placement.constant import PlacementType, OperationState


class PlacementImageSchema(Schema):
    id: int
    file: str = None


class PlacementListSchema(Schema):
    id: int
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType = Field(title="타입 ")
    operation_start: time = Field(title="운영 시간 (시작)")
    operation_end: time = Field(title="운영 시간 (끝)")
    operation_state: OperationState = Field(title="운영 상태",
                                            description="0 -운영중 1 -점검중 2 - 설치 예정")
    placement_image: List[PlacementImageSchema] = None


class PlacementInsertSchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType
    operation_start: time
    operation_end: time
    operation_state: OperationState


class PlacementModifySchema(Schema):
    placement_name: str
    placement_owner: str
    placement_address: str
    placement_type: PlacementType
    operation_start: time
    operation_end: time
    operation_state: OperationState
