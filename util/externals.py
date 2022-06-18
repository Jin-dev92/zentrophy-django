import requests
import asyncio

from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, REQUEST_PAYMENT

from order.models import Subscriptions


async def subscription_payment_test(user, customer_uid: str, merchant_uid, data):
    access_token = await asyncio.run(get_iamport_access_token())
    if type(access_token) == str:
        get_billing_key_response = await asyncio.run(get_billing_key(access_token=access_token, customer_uid=customer_uid, data=data))
        request_payment_response = await asyncio.run(request_payment(access_token=access_token, merchant_uid=merchant_uid, user=user, data=data))

    else:
        return access_token # 네이밍은 토큰으로 되어 있지만 json 형태의 리스폰스 이다.


async def get_iamport_access_token():
    token_response = requests.post(
        url=GET_TOKEN_INFO['url'],
        headers=GET_TOKEN_INFO['headers'],
        json=GET_TOKEN_INFO['data'],
        timeout=5
    )
    if token_response.json()['code'] == '0':
        access_token = token_response.json()['response'].get('access_token')
        return access_token
    else:
        return token_response.json()


async def get_billing_key(access_token: str, customer_uid: str, data):
    issue_billing_response = requests.post(
        url=ISSUE_BILLING_INFO['url'] + customer_uid,
        headers={'Authorization': access_token},
        json=data,  # SubscriptionsCreateSchema
        timeout=5
    )
    return issue_billing_response.json()


async def request_payment(access_token: str, merchant_uid: str, customer_uid: str, user, data):
    request_payment_response = requests.post(
        url=REQUEST_PAYMENT['url'],
        headers={'Authorization': access_token},
        json=data,
        timeout=5
    )
    if int(request_payment_response.json()['code']) == 0:  # 요청이 성공 했을 경우
        # DB에 저장 한다.
        Subscriptions.objects.create(
            owner=user,
            merchant_uid=merchant_uid,
            customer_uid=customer_uid
        )
    return request_payment_response.json()


async def request_payment_schedule_subscription(access_token: str, data):
    request_payment_schedule_response = requests.post(
        url='https://api.iamport.kr/subscribe/payments/schedule',
        headers={'Authorization': access_token},
        json=data,
        timeout=5
    )

    return request_payment_schedule_response.json()


async def iamport_schedule_callback(access_token: str, imp_uid: str, merchant_uid: str, user):
    # imp_uid 로 아임포트 서버에서 결제 정보 조회
    payment_response = requests.post(
                    url='https://api.iamport.kr/payments/' + imp_uid,
                    headers={'Authorization': access_token}
                )
    if int(payment_response.json()['code']) == 0 and payment_response.json()['data']:
        status = payment_response.json()['data']['response']['status']
        if status == 'paid':
            # DB에 저장하기.
            Subscriptions.objects.update_or_create(
                owner=user,
                merchant_uid=merchant_uid,
                defaults={
                    'imp_uid': imp_uid,
                    'merchant_uid': merchant_uid,
                    'response_raw': payment_response.json()
                })

    return payment_response.json()