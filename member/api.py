from typing import List, Optional

from ninja import Router
from member.schema import MemberInsertSchema, AdminInsertSchema, MemberListSchema
from member.models import Member
from django.shortcuts import get_list_or_404, get_object_or_404

from util.params import prepare_for_query

router = Router()


@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    sort: Optional[int] = None):
    params = prepare_for_query(request=request, exceptions=['sort'])
    return Member.objects.filter(**params).all().order_by()


@router.post("/", description="회원 생성")
def create_user(request, payload: MemberInsertSchema):
    return Member.objects.create(**payload.dict())


# @router.post("/admin", description="어드민 아이디 생성")
# def create_superuser(request, payload: AdminInsertSchema):  # 슈퍼유저 생성
#     return UserManager.create_superuser(**payload.dict())

@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    return get_object_or_404(Member, id=id).delete()
