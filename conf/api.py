from typing import List
from ninja import NinjaAPI

from member.models import Member
from member.schema import MemberListSchema, MemberInsertScheme
from post.constant import PostType
from post.models import Post
from post.schema import PostListScheme

api = NinjaAPI()


# memberAPI
@api.get("/member", response=List[MemberListSchema], description="DB 내의 모든 멤버 list")
def get_member_list(request):
    queryset = Member.objects.all()
    return queryset


@api.get("/member/{member_id}", response=MemberListSchema, description="id로 해당 멤버 검색")
def get_member_by_id(request, member_id: int):
    queryset = Member.objects.get(id=member_id)
    return queryset


@api.post("/member", description="멤버 생성")
def create_member(request, payload: MemberInsertScheme):
    member = Member.objects.create(**payload.dict())
    return "생성"  # todo 상태코드에 따른 response 값 스키마 작업 후 넣어주자


@api.put("/member/{member_id}", description="멤버 수정")
def modify_member(request, member_id: int, payload: MemberInsertScheme):
    qs = Member.objects.get(id=member_id)
    for attr, value in payload.dict().items():
        setattr(qs, attr, value)
        qs.save()
    return "수정"  # todo 상태코드에 따른 response 값 스키마 작업 후 넣어주자


@api.delete("/member/{member_id}", description="멤버 삭제")
def delete_member_by_id(request, member_id: int):
    queryset = Member.objects.get(id=member_id)
    queryset.delete()
    return "삭제"  # todo 상태코드에 따른 response 값 스키마 작업 후 넣어주자


# post API
@api.get("/post/{post_type}", response=List[PostListScheme], description="글 관련 데이터를 list로 가져옴. FAQ = 0, 공지사항 = 1")
def get_post_list_by_type(request, post_type: int):
    # qs = Post.objects.get(type=post_type)
    return
