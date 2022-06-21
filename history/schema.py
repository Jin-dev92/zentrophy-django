from datetime import datetime

from ninja import Field
from ninja import Schema

from history.constant import RefundMethod, RefundStatus, AfterServiceCategory, AfterServiceStatus
from member.schema import MemberListSchema
from order.schema import OrderListSchema
from placement.schema import PlacementListSchema
from product.schema import VehicleListSchema, ProductOptionsListSchema, ProductImageListSchema


class AfterServiceInsertSchema(Schema):
    place_id: int = Field(description="플레이스 아이디")
    vehicle_license: str = Field(None, description="제우스에서 갖고 오는 모터 사이클 고유 번호")
    reservation_date: datetime = Field(None, description="예약 날짜")
    detail: str = Field(None, description="상세 내용")
    category: AfterServiceCategory = Field(
        default=AfterServiceCategory.ETC,
        description="0:정기점검, 1:타이거점검, 2:브레이크 패드 점검, 3:체인 점검, 4:소모품, 5:기타"
    )


class AfterServiceListSchema(Schema):
    user: MemberListSchema = Field(None, description="유저")
    place: PlacementListSchema = Field(None, description="A/S 맡길 지점")
    registration_number: str = Field(None, description="예약 번호")
    status: AfterServiceStatus = Field(AfterServiceStatus.APPLY_WAITING, description="A/S 단계")
    reservation_date: datetime = Field(None, description="예약 날짜")
    detail: str = Field(None, description="상세 내용")
    category: AfterServiceCategory = Field(AfterServiceCategory.ETC, description="카테고리, 0:정기점검, 1:타이거점검, 2:브레이크 패드 점검, 3:체인 점검, 4:소모품, 5:기타")


class RefundLocationSchema(Schema):
    post_code: str
    address_1: str
    address_2: str = None
    address_3: str = None


class RefundListSchema(Schema):
    id: int
    order: OrderListSchema = None
    reject_reason: RefundLocationSchema = None
    method: RefundMethod = RefundMethod.RECALL_REQUEST
    status: RefundStatus = RefundStatus.WAITING


class RefundInsertSchema(Schema):
    order_id: int
    reject_reason: str = Field(None, description="환불 거절 사유, status가 환불 거절 일 때 필수.")
    refund_location: RefundLocationSchema = Field(None, description="환불 수락 시 환불 받을 위치 정보를 입력 하기 위한 컬럼")
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
    product_options: ProductOptionsListSchema = None
    product_image: str = None
    amount: int


class CartCreateSchema(Schema):
    product_options_id: int = Field(title="상품 pk")
    amount: int = Field(title="상품 수량")
