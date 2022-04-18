from typing import List, Optional

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router, Form

from conf.custom_exception import UserNotAccessDeniedException, AccessDeniedException, \
    DataBaseORMException
from member.constant import MemberSort
from member.models import User, PaymentMethod, Card
from member.schema import MemberInsertSchema, MemberListSchema, PaymentMethodListSchema, PaymentMethodInsertSchema, \
    MemberReAssignSchema
from util.params import prepare_for_query
from util.permission import has_permission

router = Router()
payment_method_router = Router()


@login_required
@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, id: Optional[int] = None, email: Optional[str] = None, username: Optional[str] = None,
                    sort: MemberSort = None):
    params = prepare_for_query(request=request, exceptions=['sort'])
    field_name = 'date_joined'
    if sort == MemberSort.RECENT:
        field_name = '-date_joined'
    if not has_permission(request):  # 어드민이 아니면
        params = {id: request.user.id}  # 위한 코드
    return User.objects.filter(**params).prefetch_related(
        Prefetch('memberownedvehicles_set', to_attr="vehicles_list"),
        Prefetch('paymentmethod_set', to_attr="payment_method")
    ).order_by(field_name)


@router.get('/{id}', description="id로 회원 찾기", response=List[MemberListSchema])
def get_member_by_id(request, id: int):
    queryset = User.objects.filter(id=id).prefetch_related(
        Prefetch('memberownedvehicles_set', to_attr="vehicles_list"),
        Prefetch('paymentmethod_set', to_attr="payment_method")
    )
    return queryset


@router.post("/", description="회원 생성", auth=None)
def create_user(request, payload: MemberInsertSchema = Form(...)):
    queryset = User.objects.create_user(**payload.dict())
    return queryset


@router.put("/", description="회원 수정", auth=None)
def modify_user(request, id: int, payload: MemberInsertSchema = Form(...)):
    if request.user == get_object_or_404(User, id=id):
        queryset = User.objects.filter(id=id).update(**payload.dict())
    else:
        raise UserNotAccessDeniedException
    return queryset


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
    member = get_object_or_404(User, id=id)
    if request.user == member or has_permission(request):
        queryset = member.delete()
        return queryset


@router.get('/forgot', description="아이디 찾기", response=str)
def forgot_id(request, username: str = Form(...), phone_number: str = Form(...)):
    return get_object_or_404(User, username=username, phone_number=phone_number).email


@router.post('/forgot', description="비밀번호 재생성")
def forgot_pwd(request, payload: MemberReAssignSchema = Form(...)):
    user = get_object_or_404(User, username=payload.dict()['username'], email=payload.dict()['email'])
    user.set_password(payload.dict()['password'])


@login_required
@payment_method_router.get('/', description="결제 수단 리스트 가져오기", response=List[PaymentMethodListSchema])
def get_payment_method(request):
    queryset = PaymentMethod.objects.get_queryset(owner=request.user).select_related('card').order_by('favorite')
    return queryset


@login_required
@transaction.atomic(using='default')
@payment_method_router.post('/', description="결제 수단 생성")
def create_payment_method(request, payload: PaymentMethodInsertSchema = Form(...)):
    # if not has_permission(request):
    #     raise LoginRequiredException

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
    get_object_or_404(PaymentMethod, owner=request.user, id=id).soft_delete()
