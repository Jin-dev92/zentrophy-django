from typing import List, Optional

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from ninja import Router, Form

from conf.custom_exception import UserNotAccessDeniedException
from member.constant import MemberSort
from member.models import User, PaymentMethod, Card, RemoteToken
from member.schema import MemberInsertSchema, MemberListSchema, PaymentMethodListSchema, PaymentMethodInsertSchema, \
    MemberReAssignSchema, MemberModifySchema
from util.params import prepare_for_query
from util.permission import has_permission, is_valid_token

router = Router()
payment_method_router = Router()


@login_required
@router.get("/", description="회원 목록", response=List[MemberListSchema])
def get_list_member(request, email: Optional[str] = None, username: Optional[str] = None,
                    sort: MemberSort = None):
    if not request.auth.is_staff:
        raise UserNotAccessDeniedException
    params = prepare_for_query(request=request, exceptions=['sort'])
    field_name = 'date_joined'
    if sort == MemberSort.RECENT:
        field_name = '-date_joined'
    return User.objects.filter(**params).prefetch_related(
        Prefetch('memberownedvehicles_set', to_attr="vehicles_list"),
        Prefetch('paymentmethod_set', to_attr="payment_method"),
    ).order_by(field_name)


@login_required
@router.get('/{id}', description="id로 회원 찾기", response=List[MemberListSchema])
def get_member_by_id(request, id: int):
    if request.auth.is_staff:
        target = User.objects.filter(id=id)
    else:
        target = User.objects.filter(id=request.auth.id)

    queryset = target.prefetch_related(
        Prefetch('memberownedvehicles_set', to_attr="vehicles_list"),
        Prefetch('paymentmethod_set', to_attr="payment_method")
    )
    return queryset


@transaction.atomic(using='default')
@router.post("/", description="회원 생성", auth=None)
def create_user(request, payload: MemberInsertSchema = Form(...)):
    try:
        member_params = {k: v for k, v in payload.dict().items() if k not in {'token_info'}}
        # token_info_params = payload.dict().get('token_info')
        user_queryset = User.objects.create_user(**member_params)
        token_queryset = RemoteToken.objects.create(
            user=user_queryset,
            access_token=None,
            refresh_token=None,
            # access_token=is_valid_token(token_info_params['access_token']),
            # refresh_token=is_valid_token(token_info_params['refresh_token']),
        )
    except Exception as e:
        raise e


@login_required
@router.put("/", description="회원 수정")
def modify_user(request, id: int, payload: MemberModifySchema = Form(...)):
    member_params = {k: v for k, v in payload.dict().items() if k not in {'token_info'}}
    target = get_object_or_404(User, id=id)
    if request.auth == target:
        user_queryset = User.objects.filter(id=id).update(**member_params)
    else:
        raise UserNotAccessDeniedException


@router.delete("/", description="회원 삭제")
def delete_user(request, id: int):
    if not request.auth.is_staff and request.auth.id != id:
        raise UserNotAccessDeniedException

    member = get_object_or_404(User, id=id)
    queryset = member.delete()


@router.post('/forgot/id', description="아이디 찾기", response=str)
def forgot_id(request, username: str = Form(...), phone_number: str = Form(...)):
    return get_object_or_404(User, username=username, phone_number=phone_number).email


@router.post('/forgot/pwd', description="비밀번호 재생성")
def forgot_pwd(request, payload: MemberReAssignSchema = Form(...)):
    user = get_object_or_404(User, username=payload.dict()['username'], email=payload.dict()['email'])
    user.set_password(payload.dict()['password'])


# @login_required
@payment_method_router.get('/', description="결제 수단 리스트 가져오기", response=List[PaymentMethodListSchema])
def get_payment_method(request):
    queryset = PaymentMethod.objects.get_queryset(owner=request.auth).select_related('card').order_by('favorite')
    return queryset


@login_required
@transaction.atomic(using='default')
@payment_method_router.post('/', description="결제 수단 생성 / 수정")
def update_or_create_payment_method(request, id: int = None, payload: PaymentMethodInsertSchema = Form(...)):
    # user = request.auth
    try:
        with transaction.atomic():
            params = payload.dict()
            card = params['card']
            card_queryset = Card.objects.create(**card)
            card_queryset.format()
            payment_queryset = PaymentMethod.objects.update_or_create(
                id=id,
                defaults={
                    'name': params['name'],
                    'owner': request.auth,
                    'card': card_queryset
                }
            )
    except Exception as e:
        raise e
        # raise DataBaseORMException


@payment_method_router.delete('/')
def delete_payment_method(request, id: int):
    get_object_or_404(PaymentMethod, owner=request.auth, id=id).soft_delete()
