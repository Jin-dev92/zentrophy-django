from typing import List
# package
from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404, get_list_or_404
# from ninja.responses import codes_4xx
from django.db import transaction
# util
from placement.constant import PlacementType
from placement.models import Placement
from placement.schema import PlacementInsertSchema, PlacementModifySchema, PlacementListSchema
from product.constant import ProductListSort
from util.util import ORJSONParser
# models & schema
# member
# from member.models import Member
# from member.schema import MemberListSchema, MemberInsertScheme
# post
from post.models import Post
from post.schema import PostListSchema, PostInsertSchema, PostModifySchema
# product
from product.models import Product, Vehicle, ProductOptions, ProductDisplayLine, VehicleColor, ProductImage
from product.schema import ProductInsertSchema, VehicleInsertSchema, ProductListSchema, ProductDisplayInsertSchema, \
    ProductDisplayLineSchema, VehicleListSchema

api = NinjaAPI(parser=ORJSONParser())
current_product_sort_state = ProductListSort.UPDATE_AT


# # member
# @api.get("/user")
# def get_user_list(request):
# queryset = auth.User.objects.all()
# return User
#
#
# @api.get("/member/{member_id}", response={200: MemberListSchema}, description="id로 해당 멤버 검색")  # todo 메시지 스키마
# def get_member_by_id(request, member_id: int):
#     queryset = get_object_or_404(Member, id=member_id)
#     return queryset
#
#
# @api.post("/member", description="멤버 생성")
# def create_member(request, payload: MemberInsertScheme):
#     Member.objects.create(**payload.dict())
#
#
# @api.put("/member/{member_id}", description="멤버 수정")
# def modify_member(request, member_id: int, payload: MemberInsertScheme):
#     qs = get_object_or_404(Member, id=member_id)
#     for attr, value in payload.dict().items():
#         setattr(qs, attr, value)
#         qs.save()
#
#
# @api.delete("/member/{member_id}", description="멤버 삭제")
# def delete_member_by_id(request, member_id: int):
#     queryset = get_object_or_404(Member, id=member_id)
#     queryset.delete()


# post
@api.get("/post/{post_type}", response={200: List[PostListSchema]},
         description="타입으로 글 관련 데이터를 obj로 가져옴. FAQ = 0, 공지사항 = 1",
         tags=["post"]
         )
def get_post_list_by_type(request, post_type: int):
    return get_list_or_404(Post, post_type=post_type)


@api.get("/post/{id}", response={200: PostListSchema},
         description="id로 글 관련 데이터를 obj로 가져옴.",
         tags=["post"]
         )
def get_post_list_by_id(request, id: int):
    qs = get_object_or_404(Post, id=id)
    return qs


@api.post("/post",
          description="글 관련 데이터 삽입",
          tags=["post"]
          )
def create_post(request, payload: PostInsertSchema):
    Post.objects.create(**payload.dict())


@api.put("/post/{id}", description="글 수정", tags=["post"])
def update_post_list_by_id(request, payload: PostModifySchema, id: int):
    qs = get_object_or_404(Post, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/post/{id}", description="글 삭제", tags=["post"])
def delete_post_by_id(request, id: int):
    get_object_or_404(Post, id=id).delete()


# product
@api.get("/product",
         description="상품 리스트 가져오기 sort 등록순: 0, 판매순 : 1 , 재고수량순: 2, 진열 라인 순: 3",
         response={200: List[ProductListSchema]},
         tags=["product"]
         )
def get_product_list(request, sort: ProductListSort):
    field_name = None
    if sort == ProductListSort.UPDATE_AT:
        field_name = "is_created"
    elif sort == ProductListSort.SALE:
        field_name = "sale_count"
    elif sort == ProductListSort.STOCK_COUNT:
        field_name = "stock_count"
    elif sort == ProductListSort.DISPLAY_LINE:
        field_name = "product_display_line"

    if sort == current_product_sort_state:
        field_name = "-" + field_name
        # current_product_sort_state.value = sort

    return Product.objects.prefetch_related(
        'product_options',
        'product_display_line',
        'product_image').all()


@api.get("/product/{id}",
         description="해당 상품 가져오기",
         response={200: ProductListSchema},
         tags=["product"]
         )
def get_product_list_by_id(request, id: int):
    return get_object_or_404(Product, id=id)


@api.post("/product", description="상품 등록", tags=["product"])
@transaction.atomic(using='default')
def create_product(request, payload: ProductInsertSchema, files: List[UploadedFile] = File(...)):
    product = {k: v for k, v in payload.dict().items() if k not in {'product_options', 'product_display_line_id'}}
    product_options = payload.dict()['product_options']
    try:
        with transaction.atomic():
            product_queryset = Product.objects.create(**product)
            product_display_line = ProductDisplayLine.objects.filter(id=payload.dict().get("product_display_line_id"))
            product_queryset.product_display_line_id.add(product_display_line.values()[0].get("id"))
            # ManyToManyField는 이런식으로 넣어줘야 됨
            for product_option in product_options:  # 프로덕트 옵션 저장
                product_options_queryset = ProductOptions.objects.create(
                    product=Product.objects.get(id=product_queryset.id),
                    option_name=product_option['option_name'],
                    stock_count=product_option['stock_count'],
                    option_description=product_option['option_description'],
                    is_apply=product_option['is_apply'],
                    product_options_label=product_option['product_options_label'],
                )
                for file in files:
                    ProductImage.objects.create(
                        product=Product.objects.get(id=product_queryset.id),
                        product_options=ProductOptions.objects.get(id=product_options_queryset.id))

    except Exception:
        return "fail : " + Exception
    return "success"


# display_line
@api.get("/display_line",
         description="상품 진열 라인 조회",
         response={200: List[ProductDisplayLineSchema]},
         tags=["product"]
         )
def get_display_line_list(request):
    return ProductDisplayLine.objects.all()


@api.post("/display_line", description="상품 진열 라인 등록", tags=["product"])
def create_display_line(request, payload: ProductDisplayInsertSchema):
    display_line = payload.dict()
    ProductDisplayLine.objects.create(
        display_line_name=display_line['display_line_name']
    )


@api.put("/display_line/{id}", tags=["product"])
def modify_display_line_by_id(request, payload: ProductDisplayInsertSchema, id: int):
    qs = get_object_or_404(ProductDisplayLine, id=id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/display_line/{id}", tags=["product"])
def delete_display_line_by_id(request, id: int):
    get_object_or_404(ProductDisplayLine, id=id).delete()


# vehicle
@api.get("/vehicle", description="모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"])
def get_vehicle_list(request):
    result = Vehicle.objects.prefetch_related('vehicle_color').all()
    return result


@api.get("/vehicle/{id}", description="id로 모터사이클 리스트", response={200: List[VehicleListSchema]}, tags=["vehicle"])
def get_vehicle_list_by_id(request, id: int):
    return get_object_or_404(Vehicle, id=id).objects.prefetch_related('vehicle_color').all()


@transaction.atomic(using='default')
@api.post("/vehicle", description="모터사이클 등록", tags=["vehicle"])
def create_vehicle(request, payload: VehicleInsertSchema):
    vehicle = {k: v for k, v in payload.dict().items() if k not in 'vehicle_color'}
    vehicle_color = payload.dict().get('vehicle_color')
    try:
        with transaction.atomic():
            vehicle_queryset = Vehicle.objects.create(**vehicle)
            for color in vehicle_color:
                VehicleColor.objects.create(
                    vehicle=Vehicle.objects.get(id=vehicle_queryset.id),
                    color_name=color['color_name'],
                    stock_count=color['stock_count'],
                    hex_code=color['hex_code'],
                    on_sale=color['on_sale'],
                    price=color['price']
                )
                # vehicle_queryset.vehicle_color_set.add(vehicle_color_queryset)
    except Exception as e:
        print(e)


@api.put("/vehicle/{id}", description="모터사이클 수정", tags=["vehicle"])
def modify_vehicle(request, payload: VehicleInsertSchema, id: int):
    qs = get_object_or_404(Vehicle, id=id).objects.prefetch_related('vehicle_color')
    # vehicle = {k: v for k, v in payload.dict().items() if k not in {'vehicle_color'}}
    # vehicle_color = payload.dict().get('vehicle_color')
    qs.update(**payload.dict())
    # .objects.update(**payload.dict())
    # for attr, value in payload.dict().items():
    #     setattr(qs, attr, value)
    # qs.save()
    return id


@api.delete("/vehicle/{id}", description="모터사이클 수정", tags=["vehicle"])
def delete_vehicle(id: int):
    get_object_or_404(Vehicle, id=id).delete()


@api.delete("/vehicle_color/{id}", description="모터사이클 수정", tags=["vehicle"])
def delete_vehicle_color(id: int):
    get_object_or_404(VehicleColor, id=id).delete()


# placement
@api.get("/place/{placement_type}",
         description="타입으로 플레이스 리스트 가져오기",
         tags=["place"],
         response={200: List[PlacementListSchema]}
         )
def get_placement_list_by_type(request, placement_type: PlacementType):
    return get_list_or_404(Placement, placement_type=placement_type)


@api.post("/place", description="플레이스 생성, # operation_start,operation_end hh:mm 형식으로 보내주세요 다른 형식도 되긴할듯", tags=["place"])
def create_placement(request, payload: PlacementInsertSchema):
    Placement.objects.create(**payload.dict())


@api.get("/place", description="플레이스 id로 해당 플레이스 정보 가져오기", response={200: List[PlacementListSchema]},
         tags=["place"])
def get_placement_list_by_id(request, id: int):
    return get_list_or_404(Placement, id=id)


@api.put("/place", description="플레이스 수정", tags=["place"])
def modify_placement(request, payload: PlacementModifySchema, id: int):
    get_object_or_404(Placement, id=id).objects.update(*payload.dict())
    # for attr, value in payload.dict().items():
    #     setattr(qs, attr, value)
    #     qs.save()


@api.delete("/place/{id}", description="플레이스 삭제", tags=["place"])
def delete_placement(request, id: int):
    get_object_or_404(Placement, id=id).delete()
