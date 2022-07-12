import asyncio
import calendar
import datetime

import requests

from conf.settings import GET_TOKEN_INFO, ISSUE_BILLING_INFO, REQUEST_PAYMENT
from order.models import Subscriptions


async def subscription_payment(owned_vehicle_id: int, data: dict, product):
    customer_uid = data.get('customer_uid')
    merchant_uid = data.get('merchant_uid')
    issue_billing = data.get('issue_billing')
    get_access_token_task = asyncio.create_task(get_iamport_access_token())
    await get_access_token_task
    if get_access_token_task.result()['code'] == 0:
        access_token = get_access_token_task.result().get('response').get('access_token')   # 토큰 획득
        if access_token:
            get_billing_key_response = asyncio.create_task(get_billing_key(
                access_token=access_token,
                customer_uid=customer_uid,
                data=issue_billing,
            ))
            await get_billing_key_response  # 빌링키 획득
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("get_billing_key_response")
            print(get_billing_key_response.result())
            if get_billing_key_response and get_billing_key_response.result().get('code') == 0:
                request_payment_response = asyncio.create_task(request_payment(access_token=access_token,
                                                                               customer_uid=customer_uid,
                                                                               merchant_uid=merchant_uid,
                                                                               amount=product.price,
                                                                               name=product.name,
                                                                               owned_vehicle_id=owned_vehicle_id,
                                                                               )
                                                               )
                await request_payment_response  # 실제 결제
                print(request_payment_response.result())
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print("request_payment_response")
                if request_payment_response:
                    if request_payment_response.result()['code'] == 0:
                        status = request_payment_response.result().get('response').get('status')
                        print(status)
                        if status and status == 'paid':
                            imp_uid = request_payment_response.result().get('response').get('imp_uid')
                            database_task = asyncio.create_task(Subscriptions.objects.create(
                                owned_vehicle_id=owned_vehicle_id,
                                merchant_uid=merchant_uid,
                                customer_uid=customer_uid,
                                imp_uid=imp_uid,
                                response_raw=request_payment_response.result(),
                            ))
                            await database_task
                            schedule_subscription_response = asyncio.create_task(request_payment_schedule_subscription( # 다음 달 결제 예약
                                access_token=access_token,
                                customer_uid=customer_uid,
                                amount=product.price,
                                name=product.name,
                                merchant_uid=merchant_uid,
                            ))

                            await schedule_subscription_response
                            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                            print("schedule_subscription_response")
                            print(schedule_subscription_response.result())
                            if schedule_subscription_response.result()['code'] != 0:
                                return schedule_subscription_response.result()
                        else:   # 결제 실패 시
                            return request_payment_response.result()
                else:
                    return request_payment_response.result()
            else:
                return get_billing_key_response.result()

            # return {  # 정기 결제 로직이 모두 성공 했을 때 성공 했을 때
            #     'get_access_token_response': get_access_token_task.result(),
            #     'get_billing_key_response': get_billing_key_response.result(),
            #     'request_payment_response': request_payment_response.result(),
            #     'schedule_subscription_response': schedule_subscription_response.result(),
            # }
        else:
            return get_access_token_task.result()
    try:
        pass
    except Exception as e:
        raise e


async def get_iamport_access_token():
    token_response = requests.post(
        url=GET_TOKEN_INFO['url'],
        headers=GET_TOKEN_INFO['headers'],
        json=GET_TOKEN_INFO['data'],
        timeout=5
    )
    return token_response.json()


async def get_billing_key(access_token: str, customer_uid: str, data: dict):
    issue_billing_response = requests.post(
        url=ISSUE_BILLING_INFO['url'] + customer_uid,
        headers={'Authorization': access_token},
        json=data,
        timeout=5
    )
    return issue_billing_response.json()


async def request_payment(access_token: str, merchant_uid: str, customer_uid: str, owned_vehicle_id: int, name: str,
                          amount: int):
    request_payment_response = requests.post(
        url=REQUEST_PAYMENT['url'],
        headers={'Authorization': access_token},
        json={
            'customer_uid': customer_uid,
            'merchant_uid': merchant_uid,
            'name': name,
            'amount': amount,

        },
        timeout=5
    )
    if request_payment_response.json()['code'] == '0':  # @todo 요청이 성공 했을 경우 callback 을 통해 해줘야 할듯?
        # DB에 저장 한다.
        imp_uid = request_payment_response.json()['response']['imp_uid']
        callback_response = await iamport_schedule_callback(
                                                      access_token=access_token,
                                                      imp_uid=imp_uid)
        if callback_response.json()['code'] == 0 and callback_response:
            Subscriptions.objects.create(
                owned_vehicle_id=owned_vehicle_id,
                merchant_uid=merchant_uid,
                customer_uid=customer_uid,
                imp_uid=imp_uid,
                response_raw=callback_response.json(),
            )
        else:
            return callback_response.json()
    return request_payment_response.json()


async def request_payment_schedule_subscription(access_token: str, customer_uid: str, amount: int, name: str,
                                                merchant_uid: str):
    current = datetime.datetime.now()

    request_payment_schedule_response = requests.post(
        url='https://api.iamport.kr/subscribe/payments/schedule',
        headers={'Authorization': access_token},
        json={
            'customer_uid': customer_uid,
            'schedules': [
                {
                    'merchant_uid': merchant_uid,
                    'amount': amount,
                    'name': name,
                    'schedule_at': (current + datetime.timedelta(days=calendar.monthrange(current.year, current.month)[1])).timestamp()
                }
            ]
        },
        timeout=5
    )
    return request_payment_schedule_response.json()


async def iamport_schedule_callback(access_token: str, imp_uid: str):
    # imp_uid 로 아임포트 서버에서 결제 정보 조회, 일반 결제, 정기 결제 둘다 쓰는듯?
    payment_response = requests.get(
        url='https://api.iamport.kr/payments/' + imp_uid,
        headers={'Authorization': access_token}
    )
    print(payment_response.json())
    return payment_response.json()


async def iamport_is_complete_get_payment_data(imp_uid: str):
    get_access_token_task = get_iamport_access_token()
    token_response = asyncio.create_task(get_access_token_task)
    await token_response
    print(token_response.result())
    access_token = token_response.result().get('response').get('access_token')
    payment_response = asyncio.create_task(iamport_schedule_callback(access_token=access_token,
                                                                     imp_uid=imp_uid))
    await payment_response
    print(payment_response.result())
    if payment_response.result().get('code') == 0:
        payment_data = payment_response.result().get('response')
        return payment_data
    else:
        return False