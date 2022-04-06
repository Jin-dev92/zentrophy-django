from datetime import datetime
from typing import List, Optional

from ninja import Schema, Field, UploadedFile, File
from pydantic import Json
from product.constant import ProductOptionsLabel, ProductLabel


# from numpy import np


class VehicleImageSchema(Schema):
    id: int
    origin_image: str = None


class ProductDisplayLineSchema(Schema):
    id: int
    display_line_name: str


class ProductDisplayInsertSchema(Schema):
    display_line_name: str


class ProductImageListSchema(Schema):
    id: int
    origin_image: str


class ProductOptionsListSchema(Schema):
    product_id: int
    option_name: str = Field(default=None,
                             title="옵션 이름")  # 옵션 이름
    stock_count: int = Field(default=0,
                             title="재고 수량")  # 재고 수량
    option_description: str = Field(default=None,
                                    title="옵션 설명")  # 옵션 설명
    is_apply: bool = Field(default=False,
                           title="옵션 적용 여부")  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel = Field(default=ProductOptionsLabel.NORMAL,
                                                       title="상품 옵션 라벨",
                                                       description="0: 기본형, 1:입력형, 2:옵션없음")  # 기본형, 입력형, 옵션없음


class ProductOptionsInsertSchema(Schema):
    option_name: str  # 옵션 이름
    stock_count: int  # 재고 수량
    option_description: str = None  # 옵션 설명
    is_apply: bool = False  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel = Field(default=ProductOptionsLabel.NORMAL,
                                                       title="0: 기본형, 1:입력형, 2:옵션없음")  # 기본형, 입력형, 옵션없음


class VehicleColorSchema(Schema):
    color_name: str = Field(title="색 이름")
    sale_count: int = Field(default=0, title="판매 수량")
    stock_count: int = Field(default=0, title="재고 수량")
    hex_code: str = Field(default="FFFFFF", title="색 코드", description="css에서 사용하는 컬러값 사용 가능, 16진수, white, rgba 값")
    on_sale: bool = Field(default=False, title="판매 여부")
    price: int = 0


class VehicleColorInsertSchema(Schema):  # 모터사이클 색상 스키마\
    vehicle_color: VehicleColorSchema = None
    # vehicle_image: List[UploadedFile] = None


class VehicleColorListSchema(Schema):
    vehicle_color: VehicleColorSchema = None
    vehicle_image: List[VehicleImageSchema] = None


class ProductInsertSchema(Schema):
    product_name: str
    product_price: int = 0
    product_label: ProductLabel = Field(default=ProductLabel.NEW,
                                        title="상품 라벨",
                                        description="0:HOT, 1:NEW, 2:SALE, 3:BEST"
                                        )  # ProductLabel.NEW
    product_options: List[ProductOptionsInsertSchema] = None  # 상품에 들어가는 상품 옵션, 여러개가 들어갈 수 있음.
    is_display: bool = Field(default=False, title="진열 여부")
    product_display_line_id: Optional[List[int]] = Field(default=None, title="상품 진열 라인 pk")
    is_refundable: bool = Field(default=False, title="환불 가능 여부")
    product_description: str = Field(default="", title="상품 설명")  # 상품 설명
    shipping_instructions: str = Field(default="", title="배송 안내")  # 배송 안내
    refund_instructions: str = Field(default="", title="환불 정책")  # 환불 정책


class VehicleListSchema(Schema):
    id: int
    vehicle_name: str
    zero_to_fifty: int
    max_speed: int
    max_output: int = Field(title="최대 출력")
    able_subsidy: bool = Field(title="기본 지원금 가능 여부")
    able_extra_subsidy: bool = Field(title="추가 지원금 가능 여부")
    is_display: bool = Field(title="진열 여부")
    vehicle_color: List[VehicleColorListSchema] = None
    # vehicle_image: List[ProductImageListSchema] = None


class VehicleInsertSchema(Schema):
    vehicle_name: str
    zero_to_fifty: int = 0
    max_speed: int = 0
    max_output: int = 0
    is_display: bool = False
    able_subsidy: bool = False
    able_extra_subsidy: bool = False
    vehicle_color: List[VehicleColorInsertSchema] = None


class ProductListSchema(Schema):
    id: int = None
    product_name: str = None
    product_price: int = None
    product_label: str = None
    is_display: bool = None
    is_refundable: bool = None
    product_description: str = Field(default="", title="상품 설명")  # 상품 설명
    shipping_instructions: str = Field(default="", title="배송 안내")  # 배송 안내
    refund_instructions: str = Field(default="", title="환불 정책")  # 환불 정책불 정책
    product_display_line: List[ProductDisplayLineSchema] = None
    product_options: List[ProductOptionsListSchema] = None
    product_image: List[ProductImageListSchema] = None
    is_created: datetime = None
    is_updated: datetime = None
