from datetime import datetime
from typing import List

from ninja import Field
from ninja import Schema
from ninja.orm import create_schema

from history.constant import RefundMethod, RefundStatus, AfterServiceCategory, AfterServiceStatus, DrivingStyle, \
    ExpendablesType, InternalCombustionEngineType
from member.schema import MemberListSchema
from order.schema import OrderListSchema
from placement.schema import PlacementListSchema
from product.constant import ProductOptionsLabel
from product.models import Product


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
    post_code: str = Field(description="우편 번호")
    address_1: str = Field(description="주소")
    address_2: str = Field(None, description="추가 주소")
    address_3: str = Field(None, description="추가 주소")


class RefundListSchema(Schema):
    id: int
    order: OrderListSchema = None
    reject_reason: RefundLocationSchema = Field(None, description="환불 사유")
    method: RefundMethod = Field(RefundMethod.RECALL_REQUEST, description="환불 방법")
    status: RefundStatus = Field(RefundStatus.WAITING, description="환불 상태(진척도)")


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


class ProductOptionsListSchemaInCart(Schema):
    id: int
    product: create_schema(Product) = None
    option_name: str = Field(default=None,
                             title="옵션 이름")  # 옵션 이름
    stock_count: int = Field(default=0,
                             title="재고 수량")  # 재고 수량
    sale_count: int = Field(default=0,
                            title="판매량")  # 재고 수량
    option_price: int = Field(default=0, description="옵션 단가")
    option_description: str = Field(default=None,
                                    title="옵션 설명")  # 옵션 설명
    is_apply: bool = Field(default=False,
                           title="옵션 적용 여부")  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel = Field(default=ProductOptionsLabel.NORMAL,
                                                       title="상품 옵션 라벨",
                                                       description="0: 기본형, 1:입력형, 2:옵션없음")  # 기본형, 입력형, 옵션없음


class CartListSchema(Schema):
    id: int
    product_options: ProductOptionsListSchemaInCart = Field(None, description="주문한 상품(product_options)")
    product_image: str = Field(None, description="상품 이미지")
    amount: int = Field(description="장 바구니에 담은 상품 갯수")


class CartCreateSchema(Schema):
    product_options_id: int = Field(title="상품 product_options_id")
    amount: int = Field(title="상품 수량")


class PrevEstimateInputCreateSchema(Schema):
    exchange_period: float = Field(description="교환 주기")
    exchange_price: float = Field(description="교환 가격")


class ExpendablesCreateSchema(PrevEstimateInputCreateSchema):
    type: ExpendablesType = Field(description="소모품 타입 // GEAR_OIL(기어 오일) = 0,FRONT_TIRE(앞 바퀴) = 1,BREAK_PAD(브레이크 패드) = 2,BACK_TIRE(뒷 바퀴) = 3, ACTUATOR (구동계)= 4")


class InternalCombustionEngineCreateSchema(PrevEstimateInputCreateSchema):
    type: InternalCombustionEngineType = Field(description="ENGINE_OIL(엔진 오일) = 0 AIR_CLEANER (에어클리너)= 1 IGNITION_PLUG(점화플러그) = 2    FRONT_TIRE(앞바퀴) = 3  MISSION_OIL(미션오일) = 4 BACK_TIRE(뒷바퀴) = 5   BREAK_PAD(브레이크패드) = 6   ACTUATOR = 7(구동계)")


class FuelRateByVehicleTypeCreateSchema(Schema):
    model_name: str = Field(description="모델 이름")
    driving_style: DrivingStyle = Field(description="운전 스타일 // HARD(격렬한) = 0, NORMAL(무난한) = 1, SAFE(안전 주행) = 2")
    fuel_rate: float = Field(description="연비")


class VehicleInfoCreateSchema(Schema):
    fuel_rate_by_vehicle_type: List[FuelRateByVehicleTypeCreateSchema] = Field(None, description="차종 별 연비")
    # avg_fuel_price: float = Field(None, description="평균 연료 가격")
    gasoline_calc: float = Field(None, description="가솔린 계수")
    electric_fuel_rate: float = Field(None, description="전비")


class PrevEstimateCreateSchema(Schema):
    vehicle_info: VehicleInfoCreateSchema = Field(None, description="자동차 정보 ( 가견적 위에 4개) ")
    expendables: List[ExpendablesCreateSchema] = Field(None, description="젠트로피 소모품")
    internal_combustion_engine: List[InternalCombustionEngineCreateSchema] = Field(None, description="내연 기관")


class PrevEstimateListSchema(Schema):
    id: int
    vehicle_info: VehicleInfoCreateSchema = Field(None, description="자동차 정보 ( 가견적 위에 4개) ")
    expendables_list: List[ExpendablesCreateSchema] = Field(None, description="젠트로피 소모품")
    internal_combustion_engine: List[InternalCombustionEngineCreateSchema] = Field(None, description="내연 기관")