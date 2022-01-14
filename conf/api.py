from typing import List
from ninja import NinjaAPI

from member.models import Member
from member.schema import MemberListSchema, MemberInsertScheme
from django.shortcuts import get_object_or_404
from post.models import Post
from post.schema import PostListScheme

# from ninja.responses import codes_4xx

api = NinjaAPI()


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
@api.get("/post/{type}", description="글 관련 데이터를 list로 가져옴. FAQ = 0, 공지사항 = 1", response={200: List[PostListScheme]})
def get_post_list_by_type(request, type: int):
    qs = get_object_or_404(Post, type=type)
    return qs
