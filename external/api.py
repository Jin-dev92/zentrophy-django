import asyncio
import datetime
import hashlib
from typing import List, Optional

import requests
from asgiref.sync import sync_to_async
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.orm import create_schema

from conf.custom_exception import WrongParameterException, ForgedOrderException
from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, DEBUG
from external.constant import Prodcd, MerchantUIDType
from order.models import Payment, Subscriptions, Order
from order.schema import InicisAuthResultSchema, TestSchema, SubscriptionsCreateSchema, \
    RequestPaymentSubscriptionsScheduleSchema
from product.models import SubscriptionProduct
from util.externals import subscription_payment, iamport_is_complete_get_payment_data, setting_async_unsafe
from util.number import generate_merchant_uid

subscription_router = Router()
payment_router = Router()
external_router = Router()


@sync_to_async
@payment_router.post('/complete/{order_id}', response=dict)
def payment_is_complete(request, order_id: int, imp_uid: str):
    '''
    일반 결제 후 콜백 함수로 불러 주는 api , 위조 검증 로직 + DB 로그 저장 기능을 한다.
    :param order_id: 주문 아이디
    :param imp_uid: 결제 아이디
    '''
    order_target = get_object_or_404(Order, id=order_id, owner=request.auth)

    if request.auth != order_target.owner:
        print("1")
        raise ForgedOrderException
    payment_data = asyncio.run(iamport_is_complete_get_payment_data(imp_uid=imp_uid))
    if not payment_data:
        print("2")
        raise ForgedOrderException

    status = payment_data.get('status')
    amount = payment_data.get('amount')
    if order_target.total == int(amount):
        Payment.objects.create(order_id=order_id, result=payment_data, merchant_uid=generate_merchant_uid(type=MerchantUIDType.PRODUCT))
    if status == 'ready':   # 가상 계좌 발급
        return {'message': '가상 계좌 발급이 완료 되었습니다.'}
    elif status == 'paid':  # 일반 결제 완료
        return {'message': '일반 결제가 완료 되었습니다.'}
    else:   # 결제 금액 불일치
        raise ForgedOrderException


@sync_to_async
@payment_router.post('/result/{order_id}', description="일반 결제 인증 결과 수신", deprecated=True)
def response_normal_payment_auth_result(request, order_id: int, payload: InicisAuthResultSchema):
    # 인증 결과를 저장 ( 로그 쌓기 )
    auth_result = payload.dict()
    merchant_uid = generate_merchant_uid(type=MerchantUIDType.PRODUCT)

    queryset = Payment.objects.create(owner=request.auth, auth_result=auth_result, order_id=order_id, merchant_uid=merchant_uid)
    if auth_result['resultCode'] == '0000':  # 성공
        try:
            auth_token = auth_result['authToken']
            auth_url = auth_result['authUrl']
            mid = auth_result['mid']
            timestamp = datetime.datetime.now().timestamp()
            signature = hashlib.sha256(('authToken=' + auth_token + '&timestamp=' + str(timestamp)).encode())
            data = {
                'authToken': auth_token,
                'timestamp': timestamp,
                'mid': mid,
                'signature': signature,
                'format': 'NVP',
            }
            response = requests.post(url=auth_url, json=data)
            response_json = response.json()
            queryset.approval_result = response_json
            queryset.save(update_fields=['approval_result'])
            return response_json
        except Exception as e:
            raise WrongParameterException
    else:   # 실패
        raise Exception("결제 결과 실패 했네? code: " + auth_result['resultCode'])


@subscription_router.get('/', description="정기 결제 리스트", response=List[create_schema(Subscriptions)])
def get_list_subscriptions(request):
    queryset = Subscriptions.objects.get_queryset()
    return queryset


@sync_to_async
@subscription_router.post('/one_time', description="나이츠 페이먼츠 정기 결제 테스트", response=Optional[dict])
def create_subscription_onetime(request, payload: TestSchema, owned_vehicle_id: int, subscription_product_id: int):
    setting_async_unsafe(True)
    try:
        product = get_object_or_404(SubscriptionProduct, id=subscription_product_id)
        task = asyncio.run(subscription_payment(owned_vehicle_id=owned_vehicle_id,
                                                data=payload.dict(),
                                                product=product),
                           debug=DEBUG)
        setting_async_unsafe(False)
        return task
    except Exception as e:
        setting_async_unsafe(False)
        raise e


@sync_to_async
@subscription_router.post('/issue_billing', description="나이츠 페이먼츠 정기 결제", deprecated=True)
def create_subscription(request, payload: SubscriptionsCreateSchema):
    params = payload.dict()
    data = {k: v for k, v in payload.dict().items() if k not in {'customer_uid'}}
    try:
        token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
        token_response_json = token_response.json()
        if int(token_response_json['code']) == 0:
            access_token = token_response_json['response'].get('access_token')
            issue_billing_response = requests.post(
                url=ISSUE_BILLING_INFO['url'] + params.get('customer_uid'),
                headers={'Authorization': access_token},
                json=data,
                timeout=5
            )
            return issue_billing_response.json()
    except Exception as e:
        raise e


@transaction.atomic(using='default')
@sync_to_async
@subscription_router.post('/payment/schedule', deprecated=True)
def request_payment_schedule_subscription(request, payload: RequestPaymentSubscriptionsScheduleSchema):
    schedules = payload.dict()['schedules']
    try:
        with transaction.atomic():
            token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
            token_response_json = token_response.json()
            if int(token_response_json['code']) == 0:
                access_token = token_response_json['response'].get('access_token')
                request_payment_schedule_response = requests.post(
                    url='https://api.iamport.kr/subscribe/payments/schedule',
                    headers={'Authorization': access_token},
                    json=payload.json(),
                    timeout=5
                )

                return request_payment_schedule_response.json()
            else:
                return token_response_json
    except Exception as e:
        raise e


@sync_to_async
@subscription_router.get('/iamport_callback/schedule', deprecated=True)
def iamport_callback(request, imp_uid: str, merchant_uid: str):
    try:
        with transaction.atomic():
            token_response = requests.post(url=GET_TOKEN_INFO['url'], headers=GET_TOKEN_INFO['headers'], json=GET_TOKEN_INFO['data'], timeout=5)
            token_response_json = token_response.json()
            if int(token_response_json['code']) == 0:
                access_token = token_response_json['response'].get('access_token')
                # imp_uid 로 아임포트 서버에서 결제 정보 조회
                payment_response = requests.post(
                    url='https://api.iamport.kr/payments/' + imp_uid,
                    headers={'Authorization': access_token}
                )
                payment_response_json = payment_response.json()
                if int(payment_response_json['code']) == 0 and payment_response_json['data']:
                    status = payment_response_json.get('data').get('response').get('status')
                    if status == 'paid':
                        # DB에 저장하기.
                        Subscriptions.objects.update_or_create(
                            # owner=request.auth,
                            merchant_uid=merchant_uid,
                            defaults={
                                'imp_uid': imp_uid,
                                'merchant_uid': merchant_uid,
                                'response_raw': payment_response_json
                            })
                return payment_response_json
            else:
                return token_response_json
    except Exception as e:
        raise e


@sync_to_async
@external_router.get('/avg_recent_price', auth=None)
def get_avg_recent_prices(request, prodcd: Prodcd = None):
    """
    공공 API 데이터, 유류 비용 평균 값
    - :param prodcd:
     ADVANCED = "B034"   # 고급 휘발유
    NORMAL = "B027" # 일반 휘발유
    DIESEL = "D047" # 경우
    KEROSENE = "C004"   # 실내 등유
    BUTAN = "K015"  #   자동차 부탄
    """
    code = 'F220426124'  #  공공 데이터 키 값
    url = 'https://www.opinet.co.kr/api/avgRecentPrice.do'
    params = {
        'code': code,
        'out': 'json',
        'prodcd': prodcd
    }
    try:
        response = requests.get(url=url, params=params, timeout=5)
        return response.json()
    except Exception as e:
        raise e
