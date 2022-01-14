from ninja import Schema

from product.constant import ProductOptionsLabel


class ProductOptions(Schema):
    option_name: str = None  # 옵션 이름
    stock_count: int = 0  # 재고 수량
    option_description: str = None  # 옵션 설명
    is_apply: bool = False  # 옵션 적용 여부
    product_options_label: ProductOptionsLabel  # 기본형, 입력형, 옵션없음


class ProductDescription(Schema):
    product_description: str = None  # 상품 설명
    shipping_instructions: str = None  # 배송 안내
    refund_instructions: str = None  # 환불 정책


class VehicleColor(Schema):  # 모터사이클 색상 스키마
    color_name: str
    stock_count: int = 0
    hex_code: str = None
    on_sale: bool = False
    price: int = 0
