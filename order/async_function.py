import requests

from conf.custom_exception import WrongParameterException
from order.schema import Subscriptions, SubscriptionsCreateSchema


def get_payments_token():
    url = "https://api.iamport.kr/users/getToken"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        'imp_key': "imp_apikey",
        'imp_secret': "ekKoeW8RyKuT0zgaZsUtXXTLQ4AhPFW3ZGseDA6bkA5lamv9OqDMnxyeB9wqOsuO9W3Mx9YSJ4dTqJ3f"
    }
    response = requests.post(url=url, headers=headers, data=data)
    response.raise_for_status()
    result = response.json()
    print(result)
    print(result.data.response)
    access_token = result.data.response.access_token
    return access_token


def get_billing(access_token: str, data: SubscriptionsCreateSchema):
    customer_uid = data['customer_uid']
    if customer_uid:
        raise WrongParameterException
    url = ' https://api.iamport.kr/subscribe/customers/' + customer_uid
    headers = {
        "Authorization": access_token
    }
    response = requests.post(url=url, headers=headers, data=data)
    response.raise_for_status()
    result = response.json()
    print(result)
    return result