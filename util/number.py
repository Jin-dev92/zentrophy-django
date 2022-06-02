import random
import string

from conf.settings import LICENSE_NUMBER_LENGTH
from history.models import AfterService

random_variation = string.digits + string.ascii_uppercase


def generate_random_number(length: int = LICENSE_NUMBER_LENGTH):  # 2. A/S 접수번호 - (랜덤생성, 16자리의 숫자 및 영문 대문자)
    global random_variation
    registration_number = "".join(random.choices(random_variation, k=length))  # 생성된 난수
    obj = AfterService.objects.filter(registration_number=registration_number).all()
    if len(obj) == 0:
        return registration_number
    else:
        generate_random_number()


def check_invalid_product_params(params: list[dict]):
    for param in params:
        filtered_dict = {k: v for k, v in param.items() if not v <= 0}
        if len(filtered_dict) == 0:
            return False
    return True