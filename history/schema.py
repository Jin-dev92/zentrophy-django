from datetime import datetime

from ninja import Schema

from history.constant import RefundMethod, RefundStatus, AfterServiceCategory
from member.schema import MemberOwnedVehiclesListSchema
from placement.schema import PlacementListSchema


class HistoryListSchema(Schema):
    id: int = None


class AfterServiceInsertSchema(Schema):
    place_id: int
    member_id: int
    reservation_date: datetime = None
    detail: str = None
    category: AfterServiceCategory = AfterServiceCategory.ETC


class AfterServiceListSchema(Schema):
    place: PlacementListSchema = None


class RefundInsertSchema(Schema):
    order_id: int
    reject_reason: str = None
    method: RefundMethod = RefundMethod.RECALL_REQUEST
    status: RefundStatus = RefundStatus.WAITING


class WarrantyInsertSchema(Schema):
    name: str
    validity: datetime
    is_warranty: bool
