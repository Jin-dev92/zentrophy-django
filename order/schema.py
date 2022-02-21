from datetime import datetime
from typing import List

from ninja import Schema, Field
from order.constant import OrderState
from member.schema import MemberListSchema


# class ExtraSubsideSchema(Schema):
#     id: int
#     name: str
#     amount: int
#     description_1: str
#     description_2: str
#
#
# class CardInfo(Schema):
#     card_no: int = None
#     payment_type: int = None
#     payment_method: int = None
#
#
# class OrderedProductInfo(Schema):  # 변경?
#     product_id: int = None
#     product_name: str = None
#     color: str = None
#     amount: str = None
#     price: int = 0
#     total_price: int = 0
#     license_code: str = None  # 상품의 경우, null, 모터사이클의 경우 리턴되는 라이센스 코드를 넣어준다.
#
#
# class OrderDeliveryInfo(Schema):  # 배송사 정보
#     delivery_name: str
#     delivery_number: str


# class OrderPaymentInfoSchema(Schema):  # 나이스 페이 결제 후 response 되는 데이터를 확인해야함
#     order_no: int
#     card_info: CardInfo = None
#     product_info: OrderedProductInfo = None
#     delivery_info: OrderDeliveryInfo = None
#     payment_detail: str = None


class OrderListSchema(Schema):
    id: int
    owner: MemberListSchema = None
    payment_info: dict = Field(title="결제 정보")
    is_able_subside: bool = Field(title="기본 보조금 가능 여부")
    extra_subside: List[int] = Field(title="추가 보조금 pk list")
    state: OrderState = Field(default=OrderState.ACCEPT_ORDER,
                              title="주문 상태",
                              description="0: 주문 수락, 1: 서류 검토중, 2: 결제 대기중, 3: 배달 준비중, 4: 배달 완료, 5: 주문 취소")
    is_created: datetime
    is_updated: datetime
    files: str = Field(default=None, title="첨부 파일")


class OrderCreateSchema(Schema):
    owner_id: int
    payment_info: dict = Field(default=None,
                               title="결제 정보",
                               description="결제 후 return 되는 결제 관련 값을 넣어줘야함. 카드번호.. 등등")
    is_able_subside: bool = False
    extra_subside_id: List[int] = Field(default=None, description="추가 보조금 pk")

# class OrderModifySchema(Schema):
#     payment_info: OrderPaymentInfoSchema = None
#     extra_subside_id: List[int] = None
