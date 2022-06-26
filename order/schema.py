from datetime import datetime, date
from typing import List

from ninja import Schema, Field

from member.schema import MemberListSchema
from order.constant import OrderState, DeliveryMethod
from product.schema import VehicleColorListSchema, ProductOptionsListSchema


class CustomerInfoSchema(Schema):
    name: str = Field(None, description="이름")
    birth: date = Field(None, description="생년월일")
    tel: str = Field(None, description="연락처")
    email: str = Field(None, description="이메일")
    is_business: bool = Field(False, description="일반 고객인지 사업자 고객인지")
    is_apply_subside: bool = Field(False, description="주문 생성 시 유저가 보조금 받을 것인가 에 대한 내용")


class OrderLocationInfoSchema(Schema):
    address_1: str = Field(None, description="우편 번호")
    address_2: str = Field(None, description="주소")
    address_3: str = Field(None, description="추가 주소")
    detail: str = Field(None, description="추가 주소")


class OrderedProductOptionsListSchema(Schema):
    product_options: ProductOptionsListSchema = None
    product_image: str = Field(None, description="상품 이미지 경로")
    amount: int = Field(None, description="주문 수량")


class OrderedVehicleColorListSchema(Schema):
    vehicle_color: VehicleColorListSchema = None
    amount: int = Field(None, description="주문 수량")


class OrderedProductOptionsCreateSchema(Schema):
    product_options_id: int = None
    amount: int = Field(None, description="주문 수량")


class OrderedVehicleColorCreateSchema(Schema):
    vehicle_color_id: int = None
    amount: int = Field(None, description="주문 수량")


class DocumentFileListSchema(Schema):
    id: int
    file: str = None


class DeliveryToSchema(Schema):
    post_code: str = Field(description="우편 번호")
    address_1: str = Field(description="주소")
    address_2: str = Field(default=None, description="추가 주소")
    address_3: str = Field(default=None, description="추가 주소")


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    ordered_product_options: List[OrderedProductOptionsListSchema] = None
    ordered_vehicle_color: List[OrderedVehicleColorListSchema] = None
    customer_info: CustomerInfoSchema = None
    order_location_info: OrderLocationInfoSchema = None
    # subside: bool = Field(default=0, title="기본 보조금")
    is_visited: bool = Field(default=False, title="방문 구매 여부")
    total: int = 0
    is_request_submit: bool = Field(default=False, description="서류 재 검토 요청 여부")
    discount_total: int = Field(default=0, description="보조금 할인 총 합계")
    delivery_method: DeliveryMethod = Field(default=DeliveryMethod.DEPEND_ON, description="배달 방법")
    delivery_to: DeliveryToSchema = Field(default=None, description="탁송 시, 배달지 주소")
    is_delivery: bool = Field(default=None, description="배송 중 여부 , True일 경우 배송 중, False 일 경우 출고 준비")
    place_remote_pk: int = Field(default=None, description="제우스에서 받아온 place_pk , delivery_method 가 직접 수령일 때 방문하는 지점의 pk 를 입력 해준다. ")
    state: OrderState = Field(default=OrderState.ACCEPT_ORDER,
                              title="주문 상태",
                              description="0: 주문 수락, 1: 서류 검토중, 2: 결제 대기중, 3: 배달 준비중, 4: 배달 완료, 5: 주문 취소")
    files: List[DocumentFileListSchema] = Field(default=None, title="첨부 파일")
    is_created: datetime
    is_updated: datetime


class OrderCreateSchema(Schema):
    ordered_product_options: List[OrderedProductOptionsCreateSchema] = Field(default=None, description="주문할 상품 옵션 > 해당 사항 없으면 보내지 마세요")
    ordered_vehicle_color: List[OrderedVehicleColorCreateSchema] = Field(default=None, description="주문할 모터 사이클 색깔 > 해당 사항 없으면 보내지 마세요")
    customer_info: CustomerInfoSchema = None
    order_location_info: OrderLocationInfoSchema = None
    subside: bool = Field(default=False, description="기본 보조금 여부")
    extra_subside: List[int] = Field(default=None, description="추가 보조금 pk")
    total: int = 0
    is_visited: bool = Field(default=False, description="방문 구매 여부")


class ExtraSubsideListSchema(Schema):
    id: int
    name: str = Field(None, description="추가 보조금 이름")
    amount: int = Field(0, description="추가 보조금 액수")
    description_1: str = ""
    description_2: str = ""


class ExtraSubsideInsertSchema(Schema):
    name: str = Field(description="추가 보조금 이름")
    amount: int = Field(0, description="추가 보조금 액수")
    description_1: str = ""
    description_2: str = ""


class SubsideListSchema(Schema):
    id: int
    amount: int = Field(0, description="기본 보조금 액수")
    extra: List[ExtraSubsideListSchema] = None


class SubsideInsertSchema(Schema):
    amount: int = Field(0, description="기본 보조금 액수")
    extra: List[ExtraSubsideInsertSchema] = Field(None, description="추가 보조금 아이디 리스트")


class DocumentFormatListSchema(Schema):
    id: int
    file: str = None


class ApplySubSideSchema(Schema):
    extra_subside: List[int] = Field(default=None, description="추가 보조금 pk")


class DeliveryMethodInputSchema(Schema):
    delivery_method: DeliveryMethod = Field(None, description="DEPEND_ON(탁송) = 0, YOURSELF(직접 수령) = 1")
    delivery_to: DeliveryToSchema = None
    place_remote_pk: int = Field(None, description="제우스에서 갖고 오는 플레이스 Pk")


class InicisAuthResultSchema(Schema):
    resultCode: str
    resultMsg: str = None
    mid: str
    orderNumber: str = None
    authToken: str
    authUrl: str
    netCancelUrl: str = None
    charset: str = None
    merchantData: str = None


class SubscriptionsSchema(Schema):
    card_number: str = Field(description="카드 번호 12자리")
    expiry: str = Field(description="카드 유효기간")
    birth: str = Field(description="생년월일")
    pwd_2digit: str = Field(description="카드 비밀번호 앞 두자리")


class SubscriptionsCreateSchema(SubscriptionsSchema):
    customer_uid: str


class RequestPaymentSubscriptionsSchema(Schema):
    customer_uid: str
    merchant_uid: str
    amount: int
    name: str


class Schedule(Schema):
    merchant_uid: str
    schedule_at: int = Field(description="결제 시도 시각, 타임스탬프로 보내기")
    amount: int
    name: str
    buyer_name: str
    buyer_tel: str
    buyer_email: str


class RequestPaymentSubscriptionsScheduleSchema(Schema):
    customer_uid: str
    schedules: List[Schedule]


class TestSchema(Schema):
    customer_uid: str
    issue_billing: SubscriptionsSchema = None
    payment_subscription: RequestPaymentSubscriptionsSchema = None
    schedules: RequestPaymentSubscriptionsScheduleSchema = None
