import asyncio

import requests

from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, REQUEST_PAYMENT
from order.models import Subscriptions


async def subscription_payment_test(user, merchant_uid: str, owned_vehicle_id: int, data: dict):
    customer_uid = data.get('customer_uid')
    issue_billing_data = data.get('customer_uid')
    payment_subscription_data = data.get('payment_subscription')
    schedules_data = data.get('schedules')
    get_access_token_task = asyncio.create_task(get_iamport_access_token())
    await get_access_token_task
    if get_access_token_task.result()['code'] == 0:
        access_token = get_access_token_task.result()['response'].get('access_token')
        if type(access_token) == str:
            get_billing_key_response = asyncio.create_task(get_billing_key(
                access_token=access_token,
                customer_uid=customer_uid,
                data=issue_billing_data))
            request_payment_response = asyncio.create_task(request_payment(access_token=access_token,
                                                                           customer_uid=customer_uid,
                                                                           merchant_uid=merchant_uid,
                                                                           owned_vehicle_id=owned_vehicle_id,
                                                                           user=user, data=payment_subscription_data))
            schedule_subscription_response = asyncio.create_task(request_payment_schedule_subscription(
                access_token=access_token,
                data=schedules_data))
            await get_billing_key_response
            await request_payment_response
            await schedule_subscription_response
            return {
                'get_access_token_response': get_access_token_task.result(),
                'get_billing_key_response': get_billing_key_response.result(),
                'request_payment_response': request_payment_response.result(),
                'schedule_subscription_response': schedule_subscription_response.result(),
            }
        else:
            return get_access_token_task.result()


async def get_iamport_access_token():
    token_response = requests.post(
        url=GET_TOKEN_INFO['url'],
        headers=GET_TOKEN_INFO['headers'],
        json=GET_TOKEN_INFO['data'],
        timeout=5
    )
    return token_response.json()


async def get_billing_key(access_token: str, customer_uid: str, data):
    issue_billing_response = requests.post(
        url=ISSUE_BILLING_INFO['url'] + customer_uid,
        headers={'Authorization': access_token},
        json=data,  # SubscriptionsCreateSchema
        timeout=5
    )
    return issue_billing_response.json()


async def request_payment(access_token: str, merchant_uid: str, customer_uid: str, owned_vehicle_id: int, user, data):
    request_payment_response = requests.post(
        url=REQUEST_PAYMENT['url'],
        headers={'Authorization': access_token},
        json=data,
        timeout=5
    )
    if int(request_payment_response.json()['code']) == 0:  # 요청이 성공 했을 경우
        # DB에 저장 한다.
        Subscriptions.objects.create(
            owned_vehicle_id=owned_vehicle_id,
            # owner=user,
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
                # owner=user,
                merchant_uid=merchant_uid,
                defaults={
                    'imp_uid': imp_uid,
                    'merchant_uid': merchant_uid,
                    'response_raw': payment_response.json()
                })

    return payment_response.json()


async def iamport_is_complete_payment(imp_uid):
    get_access_token_task = get_iamport_access_token()
    token_response: dict = asyncio.create_task(get_access_token_task).result()
    access_token = token_response.get('response').get('access_token')
    payment_url = 'https://api.iamport.kr/payments/' + imp_uid
    payment_response: dict = asyncio.create_task(requests.get(
        url=payment_url,
        headers={"Authorization": access_token},
        timeout=5).json()).result()
    payment_data: dict = payment_response.get('response')
    status = payment_data.get('status')
    amount = payment_data.get('amount')

    # try:
    #     token_response = requests.post(
    #         url=GET_TOKEN_INFO['url'],
    #         headers=GET_TOKEN_INFO['headers'],
    #         json=GET_TOKEN_INFO['data'],
    #         timeout=5
    #     )
    #     token_response_json: dict = token_response.json()
    #     if token_response_json and token_response_json.get('response'):
    #         access_token = token_response_json.get('response').get('access_token')
    #         payment_url = 'https://api.iamport.kr/payments/' + imp_uid
    #         payment_response = requests.get(
    #             url=payment_url,
    #             headers={"Authorization": access_token},
    #             timeout=5)
    #
    #         payment_response_json = payment_response.json()
    #         if payment_response_json and payment_response_json.get('response'):
    #             payment_data = payment_response_json.get('response')
    #             status = payment_data.get('status')
    #             amount = payment_data.get('amount')
    #             if order_target.total == int(amount):
    #                 Payment.objects.create(order_id=order_id, result=payment_data, merchant_uid=merchant_uid)
    #                 if status == 'ready':   # 가상 계좌 발급
    #                     return {'message': '가상 계좌 발급이 완료 되었습니다.'}
    #                 elif status == 'paid':  # 일반 결제 완료
    #                     return {'message': '일반 결제가 완료 되었습니다.'}
    #                 else:   # 결제 금액 불일치
    #                     raise ForgedOrderException
    #         else:
    #             return payment_response_json
    # except Exception as e:
    #     raise e