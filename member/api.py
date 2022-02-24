from typing import List, Optional

from ninja import Router, Form
from ninja.responses import Response

from member.schema import MemberInsertSchema, MemberListSchema
from member.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, authenticate
from util.default import ResponseDefaultHeader
from util.params import prepare_for_query

router = Router()


@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    # sort: Optional[int] = None
                    ):
    params = prepare_for_query(request=request, exceptions=['sort'])
    return User.objects.filter(**params).all().order_by(**params)


@router.post("/", description="회원 생성", response=ResponseDefaultHeader.Schema, auth=None)
def create_user(request, payload: MemberInsertSchema):
    queryset = User.objects.create_user(**payload.dict())
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="유저 생성이 되었습니다.",
        data=queryset
    )


@router.get('/logout', description="로그 아웃")
def member_logout(request):
    logout(request)
    return {200: "로그 아웃이 되었습니다."}


@router.post("/login", description="로그인", auth=None)
def member_login(request, email: str = Form(...), password: str = Form(...)):
    params = prepare_for_query(request)
    user = authenticate(request, **params)
    if user is not None:
        login(request, user)
    else:
        raise ValueError('아이디 혹은 비밀번호가 틀립니다.')


@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    return get_object_or_404(User, id=id).delete()
