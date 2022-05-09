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


class BatteryExchangeInsertSchema(Schema):
    place_id: int = Field(title="플레이스 pk")
    order_id: int = Field(title="주문 pk")
    member_owned_vehicles_id: int = Field(title="회원 보유 모터 사이클 pk")
    fee_plan_id: int = Field(title="요금제 pk")
    used_battery: float = Field(default=0, title="누적 사용량")


class CartListSchema(Schema):  # todo 데이터 형식에 맞게 수정해둬야함
    id: int
    product: str
    amount: int


class CartCreateSchema(Schema):
    product_id: int = Field(title="상품 pk")
    amount: int = Field(title="상품 수량")
