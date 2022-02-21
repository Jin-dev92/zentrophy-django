from typing import List, Optional

from ninja import Router
from member.schema import MemberInsertSchema, MemberListSchema
from member.models import User
from django.shortcuts import get_object_or_404
from util.params import prepare_for_query

router = Router()


@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    sort: Optional[int] = None):
    params = prepare_for_query(request=request, exceptions=['sort'])
    return User.objects.filter(**params).all().order_by()


@router.post("/", description="회원 생성")
def create_user(request, payload: MemberInsertSchema):
    print("@@@@@@@@@@")
    print(payload)
    print(type(payload))
    # return Member.objects.create_user(pay)


@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    return get_object_or_404(User, id=id).delete()
