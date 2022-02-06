from typing import List

from ninja import Router
from member.schema import MemberInsertSchema, AdminInsertSchema, MemberListSchema
from member.models import Member
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.models import UserManager

router = Router()


@router.get("", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request):
    return Member.objects.all()


@router.get("", description="특정 회원 pk로 찾기", response=MemberListSchema)
def get_list_member_by_id(request):
    return get_object_or_404(Member, id=id)


@router.post("", description="회원 생성")
def create_user(request, payload: MemberInsertSchema):
    Member.objects.create(**payload.dict())


@router.post("/admin", description="어드민 아이디 생성")
def create_superuser(request, payload: AdminInsertSchema):  # 슈퍼유저 생성
    return UserManager.create_superuser(**payload.dict())
