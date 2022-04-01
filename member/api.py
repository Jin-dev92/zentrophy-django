from typing import List, Optional

from django.contrib.auth import login, logout, authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router, Form
from ninja.responses import Response

from conf.custom_exception import UserNotAccessDeniedException, LoginRequiredException, AccessDeniedException, \
    DataBaseORMException
from member.constant import MemberSort
from member.models import User, PaymentMethod, Card
from member.schema import MemberInsertSchema, MemberListSchema, PaymentMethodListSchema, PaymentMethodInsertSchema, \
    MemberReAssignSchema
from util.default import ResponseDefaultHeader
from util.params import prepare_for_query
from util.permission import has_permission

router = Router()
payment_method_router = Router()


@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    sort: MemberSort = None):
    params = prepare_for_query(request=request, exceptions=['sort'])
    field_name = 'date_joined'
    if sort == MemberSort.RECENT:
        field_name = '-date_joined'

    if has_permission(request):
        return User.objects.filter(**params).all().order_by(field_name)
    else:  # 내 정보에서 호출해주기 위한 코드
        if len(User.objects.filter(id=request.user.id)) == 0:
            raise LoginRequiredException
        else:
            return User.objects.filter(id=request.user.id)


@router.post("/", description="회원 생성", response=ResponseDefaultHeader.Schema, auth=None)
def create_user(request, payload: MemberInsertSchema):
    queryset = User.objects.create_user(**payload.dict())
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="유저 생성이 되었습니다.",
    )


@router.put("/", description="회원 수정", response=ResponseDefaultHeader.Schema, auth=None)
def modify_user(request, payload: MemberInsertSchema):
    if has_permission(request):
        User.objects.update(**payload.dict())
    else:
        raise UserNotAccessDeniedException
    return ResponseDefaultHeader(
        code=Response.status_code,
        message="유저 수정이 되었습니다.",
    )


@router.get('/logout', description="로그 아웃")
def member_logout(request):
    logout(request)


@router.post("/login", description="로그인", auth=None)
def member_login(request, email: str = Form(...), password: str = Form(...)):
    user = authenticate(request, email=email, password=password)
    if user is None:
        raise AccessDeniedException
    login(request, user)


@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    user = request.user
    if not has_permission(request):  # 일반 유저 일 때
        target = get_object_or_404(User, id=id)
        if user != target:  # 일반 유저가 다른 유저의 계정을 삭제 하기 못하게 하기 위한 코드
            raise UserNotAccessDeniedException
    get_object_or_404(User, id=id).delete()


@router.get('/forgot', description="아이디 찾기", response=str)
def forgot_id(request, username: str, phone_number: str):
    return get_object_or_404(User, username=username, phone_number=phone_number).email


@router.post('/forgot', description="비밀번호 재생성")
def forgot_pwd(request, payload: MemberReAssignSchema):
    user = get_object_or_404(User, username=payload.dict()['username'], email=payload.dict()['email'])
    user.set_password(payload.dict()['password'])


@payment_method_router.get('/', description="결제 수단 리스트 가져오기", response=Optional[List[PaymentMethodListSchema]])
def get_payment_method(request):
    if has_permission(request):
        return PaymentMethod.objects.get_queryset(owner=request.user).select_related('card').all().order_by('favorite')
    else:
        return []


@transaction.atomic(using='default')
@payment_method_router.post('/', description="결젤 수단 생성")
def create_payment_method(request, payload: PaymentMethodInsertSchema):
    if not has_permission(request):
        raise LoginRequiredException

    try:
        with transaction.atomic():
            payment_method = PaymentMethod.objects.update_or_create(
                name=payload.dict()['name'],
                owner=request.user
            )
            card = Card.objects.update_or_create(**payload.dict()['card'])
            payment_method[0].card = card[0]
            payment_method[0].save()
    except Exception as e:
        raise DataBaseORMException


@payment_method_router.delete('/')
def delete_payment_method(request, id: int):
    get_object_or_404(PaymentMethod, id=id).soft_delete()
