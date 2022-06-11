from datetime import datetime

from ninja import Field
from ninja import Schema

from history.constant import RefundMethod, RefundStatus, AfterServiceCategory, AfterServiceStatus
from member.schema import MemberListSchema
from order.schema import OrderListSchema
from placement.schema import PlacementListSchema
from product.schema import VehicleListSchema


class AfterServiceInsertSchema(Schema):
    place_id: int
    owned_vehicle_id: int
    registration_number: str = None
    reservation_date: datetime = None
    detail: str = None
    category: AfterServiceCategory = Field(
        default=AfterServiceCategory.ETC,
        description="0:정기점검, 1:타이거점검, 2:브레이크 패드 점검, 3:체인 점검, 4:소모품, 5:기타"
    )


class AfterServiceListSchema(Schema):
    user: MemberListSchema = None
    place: PlacementListSchema = None
    owned_vehicle: VehicleListSchema = None
    registration_number: str = None
    status: AfterServiceStatus = AfterServiceStatus.APPLY_WAITING
    reservation_date: datetime
    detail: str = None
    category: AfterServiceCategory = AfterServiceCategory.ETC


class RefundListSchema(Schema):
    id: int
    order: OrderListSchema = None
    reject_reason: str = None
    method: RefundMethod = RefundMethod.RECALL_REQUEST
    status: RefundStatus = RefundStatus.WAITING


class RefundInsertSchema(Schema):
    order_id: int
    reject_reason: str = None
    refund_location: str = None
    method: RefundMethod = Field(
        title="환불 방법",
        default=RefundMethod.RECALL_REQUEST,
        description="0: RECALL_REQUEST, 1: Direct"
    )
    status: RefundStatus = Field(
        title="환불 상태",
        default=RefundStatus.WAITING,
        description="0: 환불 대기, 1: 환불 완료, 2:환불 수락, 3: 환불 거절"
    )


class WarrantyListSchema(Schema):
    id: int
    name: str
    validity: datetime = Field(title="유효기간")
    is_warranty: bool = Field(title="보증 가능 여부")


class WarrantyInsertSchema(Schema):
    name: str
    validity: datetime = Field(title="유효기간")
    is_warranty: bool = Field(title="보증 가능 여부 // True = 보증 가능, False = 보증 제외")


class CartListSchema(Schema):
    id: int
    product_options: str = None
    amount: int


class CartCreateSchema(Schema):
    product_options_id: int = Field(title="상품 pk")
    amount: int = Field(title="상품 수량")
