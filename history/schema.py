from datetime import datetime

from ninja import Field
from ninja import Schema

from history.constant import RefundMethod, RefundStatus, AfterServiceCategory
from placement.schema import PlacementListSchema


class HistoryListSchema(Schema):
    id: int = None


class AfterServiceInsertSchema(Schema):
    place_id: int
    member_id: int
    reservation_date: datetime = None
    detail: str = None
    category: AfterServiceCategory = Field(
        default=AfterServiceCategory.ETC,
        description="0:정기점검, 1:타이거점검, 2:브레이크 패드 점검, 3:체인 점검, 4:소모품, 5:기타"
    )


class AfterServiceListSchema(Schema):
    place: PlacementListSchema = None


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


class WarrantyInsertSchema(Schema):
    name: str
    validity: datetime = Field(title="유효기간")
    is_warranty: bool = Field(title="보증 가능 여부")


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
