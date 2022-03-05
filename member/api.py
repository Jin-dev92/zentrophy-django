from typing import List, Optional

from ninja import Router, Form
from ninja.responses import Response

from member.schema import MemberInsertSchema, MemberListSchema, PaymentMethodListSchema, PaymentMethodInsertSchema
from member.models import User, PaymentMethod, Card
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, authenticate

from util.default import ResponseDefaultHeader
from util.exception.exception import USER_NOT_ACCESS_DENIED, LoginRequiredException
from util.params import prepare_for_query
from util.permission import has_permission

router = Router()
payment_method_router = Router()


@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    # sort: Optional[int] = None
                    ):
    params = prepare_for_query(request=request, exceptions=['sort'])
    if has_permission(request):
        return User.objects.filter(**params).all().order_by()
    else:  # 내정보에서 호출해주기 위한 코드
        return User.objects.filter(id=request.user.id)


@router.post("/", description="회원 생성", response=ResponseDefaultHeader.Schema, auth=None)
def create_user(request, payload: MemberInsertSchema):
    queryset = User.objects.create_user(**payload.dict())
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="유저 생성이 되었습니다.",
    )


@router.get('/logout', description="로그 아웃")
def member_logout(request):
    logout(request)
    return {200: "로그 아웃이 되었습니다."}


@router.post("/login", description="로그인", auth=None)
def member_login(request, email: str = Form(...), password: str = Form(...)):
    user = authenticate(request, email=email, password=password)
    if user is None:
        raise ValueError('아이디 혹은 비밀번호가 틀립니다.')
    login(request, user)


@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    user = request.user
    if has_permission(request) is False:  # 일반 유저 일 때
        target = get_object_or_404(User, id=id)
        if user != target:  # 일반 유저가 다른 유저의 계정을 삭제 하기 못하게 하기 위한 코드
            raise USER_NOT_ACCESS_DENIED

    return get_object_or_404(User, id=id).delete()


@payment_method_router.get('/', description="결제 수단 리스트 가져오기", response=Optional[List[PaymentMethodListSchema]])
def get_payment_method(request):
    if has_permission(request):
        return PaymentMethod.objects.filter(owner=request.user).select_related('card').all().order_by('favorite')
    else:
        return []


@payment_method_router.post('/', description="결젤 수단 생성")
def create_payment_method(request, payload: PaymentMethodInsertSchema):
    print(type(payload))
    if has_permission(request):
        payment_method = PaymentMethod.objects.update_or_create(
            name=payload.dict()['name'],
            owner=request.user
        )
        card = Card.objects.update_or_create(**payload.dict()['card'])
        payment_method[0].card = card
        payment_method[0].save()
    else:
        raise LoginRequiredException


@payment_method_router.delete('/')
def delete_payment_method(request, id: int):
    return get_object_or_404(PaymentMethod, id=id).delete()
