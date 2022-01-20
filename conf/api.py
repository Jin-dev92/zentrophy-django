from typing import List
# package
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
# from ninja.responses import codes_4xx

# util
from placement.models import Placement
from placement.schema import PlacementInsertSchema, PlacementModifySchema
from util.util import ORJSONParser, ORJSONRenderer
# models & schema
# member
from member.models import Member
from member.schema import MemberListSchema, MemberInsertScheme
# post
from post.models import Post
from post.schema import PostListSchema, PostInsertSchema, PostModifySchema
# product
from product.models import Product, Vehicle, ProductOptions, ProductDisplayLine
from product.schema import ProductInsertSchema, VehicleInsertSchema, ProductListSchema, ProductDisplayInsertSchema, \
    ProductDisplayLineSchema, VehicleListSchema

api = NinjaAPI(parser=ORJSONParser())


# member
@api.get("/member", response={200: List[MemberListSchema]}, description="DB 내의 모든 멤버 list")
def get_member_list(request):
    queryset = Member.objects.all()
    return queryset


@api.get("/member/{member_id}", response={200: MemberListSchema}, description="id로 해당 멤버 검색")  # todo 메시지 스키마
def get_member_by_id(request, member_id: int):
    queryset = get_object_or_404(Member, id=member_id)
    return queryset


@api.post("/member", description="멤버 생성")
def create_member(request, payload: MemberInsertScheme):
    Member.objects.create(**payload.dict())


@api.put("/member/{member_id}", description="멤버 수정")
def modify_member(request, member_id: int, payload: MemberInsertScheme):
    qs = get_object_or_404(Member, id=member_id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/member/{member_id}", description="멤버 삭제")
def delete_member_by_id(request, member_id: int):
    queryset = get_object_or_404(Member, id=member_id)
    queryset.delete()


# post
@api.get("/post/{post_type}", response={200: PostListSchema},
         description="타입으로 글 관련 데이터를 obj로 가져옴. FAQ = 0, 공지사항 = 1")
def get_post_list_by_type(request, post_type: int):
    qs = get_object_or_404(Post, post_type=post_type)
    return qs


@api.get("/post/{id}", response={200: PostListSchema},
         description="id로 글 관련 데이터를 obj로 가져옴.")
def get_post_list_by_id(request, id: int):
    qs = get_object_or_404(Post, id=id)
    return qs


@api.post("/post", description="글 관련 데이터 삽입")
def create_post(request, payload: PostInsertSchema):
    Post.objects.create(**payload.dict())


@api.put("/post/{id}", description="글 수정")
def update_post_list_by_id(request, payload: PostModifySchema, id: int):
    qs = get_object_or_404(Post, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/post/{id}", description="글 삭제")
def delete_post_by_id(request, id: int):
    get_object_or_404(Post, id=id).delete()


# product
@api.get("/product", description="상품 리스트 가져오기", response={200: List[ProductListSchema]})
def get_product_list(request):
    return Product.objects.all()


@api.get("/product/{id}", description="해당 상품 리스트 가져오기", response={200: List[ProductListSchema]})
def get_product_list_by_id(request, id: int):
    get_object_or_404(Product, id=id)


@api.post("/product", description="상품 등록")
def create_product(request, payload: ProductInsertSchema):
    product = payload.dict()
    print("@@@@@@@@@")
    print(product['description'])
    product_queryset = Product.objects.create(
        product_name=product['product_name'],
        product_price=product['product_price'],
        product_label=product['product_label'],
        is_display=product['is_display'],
        product_display_line_id=product['product_display_line_id'],
        is_refundable=product['is_refundable'],
        description=product['description']
    )

    for product_option in product['product_options']:
        ProductOptions.objects.create(
            product_id=product_queryset.id,
            option_name=product_option['option_name'],
            stock_count=product_option['stock_count'],
            option_description=product_option['option_description'],
            is_apply=product_option['is_apply'],
            product_options_label=product_option['product_options_label']
        )


# display_line
@api.get("/display_line", description="상품 진열 라인 조회", response={200: List[ProductDisplayLineSchema]})
def get_display_line_list(request):
    return ProductDisplayLine.objects.all()


@api.post("/display_line", description="상품 진열 라인 등록")
def create_display_line(request, payload: ProductDisplayInsertSchema):
    ProductDisplayLine.objects.create(
        display_line_name=payload.dict()['display_line_name']
    )


# vehicle
@api.get("/vehicle", description="모터사이클 리스트", response=List[VehicleListSchema])
def get_vehicle_list(request):
    return Vehicle.objects.all()


@api.get("/vehicle/{id}", description="모터사이클 리스트", response=List[VehicleListSchema])
def get_vehicle_list_by_Id(request, id: int):
    return get_object_or_404(Vehicle, id=id)


@api.post("/vehicle", description="모터사이클 등록")
def create_vehicle(request, payload: VehicleInsertSchema):
    vehicle = payload.dict()


# placement
@api.post("/place", description="플레이스 생성")
def create_placement(request, payload: PlacementInsertSchema):
    Placement.objects.create(**payload.dict())


@api.put("/place/{id}", description="플레이스 수정")
def modify_placement(request, payload: PlacementModifySchema, id: int):
    qs = get_object_or_404(Placement, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/place/{id}", description="플레이스 삭제")
def delete_placement(request, id: int):
    get_object_or_404(Placement, id=id).delete()
