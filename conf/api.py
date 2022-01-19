import json
from typing import List
# package
import orjson
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
# from ninja.responses import codes_4xx

# util
from util.util import ORJSONParser, ORJSONRenderer
# models & schema
# member
from member.models import Member
from member.schema import MemberListSchema, MemberInsertScheme
# post
from post.models import Post
from post.schema import PostListSchema, PostInsertSchema, PostModifySchema
# product
from product.models import Product, Vehicle
from product.schema import ProductInsertSchema, VehicleInsertSchema

api = NinjaAPI(parser=ORJSONParser(), renderer=ORJSONRenderer)


# memberAPI
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
    qs = get_object_or_404(id=member_id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/member/{member_id}", description="멤버 삭제")
def delete_member_by_id(request, member_id: int):
    queryset = get_object_or_404(Member, id=member_id)
    queryset.delete()


# post API
@api.get("/post/{type}", description="글 관련 데이터를 obj로 가져옴. FAQ = 0, 공지사항 = 1", response={200: List[PostListSchema]})
def get_post_list_by_type(request, type: int):
    qs = get_object_or_404(Post, type=type)
    return qs


@api.post("/post", description="글 관련 데이터 삽입")
def create_post(request, payload: PostInsertSchema):
    Post.objects.create(**payload.dict())


@api.put("/post/{no}", description="글 수정")
def update_post_list_by_type(request, payload: PostModifySchema, no: int):
    qs = get_object_or_404(no=no)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()


@api.delete("/post/{no}", description="글 삭제")
def delete_member_by_id(request, no: int):
    queryset = get_object_or_404(Member, id=no)
    queryset.delete()


@api.post("/product", description="상품 등록")
def create_product(request, payload: ProductInsertSchema):
    Product.objects.create(**payload.dict())


@api.post("/vehicle", description="모터사이클 등록")
def create_vehicle(request, payload: VehicleInsertSchema):
    Vehicle.objects.create(**payload.dict())
