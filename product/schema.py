from datetime import datetime
from typing import List, Optional
from pydantic.color import Color
from ninja import Schema
# from numpy import np

from product.constant import ProductOptionsLabel, ProductLabel


class VehicleImageSchema(Schema):
    origin_image: str = None


class ProductDisplayLineSchema(Schema):
    id: int
    display_line_name: str


class ProductDisplayInsertSchema(Schema):
    display_line_name: str


class ProductImageListSchema(Schema):
    origin_image: str = None


class ProductOptionsListSchema(Schema):
    product_id: int
    option_name: str = None  # 옵션 이름
    stock_count: int = 0  # 재고 수량
    option_description: str = None  # 옵션 설명
    is_apply: bool = False  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel = ProductOptionsLabel.NORMAL  # 기본형, 입력형, 옵션없음


class ProductOptionsInsertSchema(Schema):
    option_name: str  # 옵션 이름
    stock_count: int  # 재고 수량
    option_description: str = None  # 옵션 설명
    is_apply: bool = False  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel = ProductOptionsLabel.NORMAL  # 기본형, 입력형, 옵션없음


class ProductDescription(Schema):
    product_description: str = ""  # 상품 설명
    shipping_instructions: str = ""  # 배송 안내
    refund_instructions: str = ""  # 환불 정책


class VehicleColor(Schema):  # 모터사이클 색상 스키마\
    color_name: str
    stock_count: int = 0
    hex_code: str = None
    on_sale: bool = False
    price: int = 0


class ProductInsertSchema(Schema):
    product_name: str
    product_price: int = 0
    product_label: ProductLabel = ProductLabel.NEW  # ProductLabel.NEW
    product_options: List[ProductOptionsInsertSchema] = None  # 상품에 들어가는 상품 옵션, 여러개가 들어갈 수 있음.
    is_display: bool = False
    product_display_line_id: Optional[List[int]] = None
    is_refundable: bool = False
    description: ProductDescription = None


class VehicleListSchema(Schema):
    id: int
    vehicle_name: str
    zero_to_fifty: int
    max_speed: int
    max_output: int
    able_subsidy: bool
    able_extra_subsidy: bool
    is_display: bool
    vehicle_color: List[VehicleColor] = None
    vehicle_image: List[ProductImageListSchema] = None


class VehicleInsertSchema(Schema):
    vehicle_name: str
    zero_to_fifty: int = 0
    max_speed: int = 0
    max_output: int = 0
    is_display: bool = False
    able_subsidy: bool = False
    able_extra_subsidy: bool = False
    vehicle_color: List[VehicleColor] = None


class ProductListSchema(Schema):
    id: int = None
    product_name: str = None
    product_price: int = None
    product_label: str = None
    is_display: bool = None
    is_refundable: bool = None
    description: ProductDescription = None
    product_display_line: List[ProductDisplayLineSchema] = None
    product_options: List[ProductOptionsListSchema] = None
    product_image: List[ProductImageListSchema] = None
    is_created: datetime = None
    is_updated: datetime = None
