import datetime
import random
import string

from conf.settings import LICENSE_NUMBER_LENGTH
from history.models import AfterService

# from member.models import OwnedVehicle

random_variation = string.digits + string.ascii_uppercase


def generate_after_service_number(length: int = LICENSE_NUMBER_LENGTH):  # 2. A/S 접수번호 - (랜덤생성, 16자리의 숫자 및 영문 대문자)
    global random_variation
    registration_number = "".join(random.choices(random_variation, k=length))  # 생성된 난수
    obj = AfterService.objects.filter(registration_number=registration_number).all()
    if len(obj) == 0:
        return registration_number
    else:
        generate_after_service_number()


def generate_release_number():
    global random_variation
    registration_number = "".join(random.choices(random_variation, k=6))
    number = datetime.datetime.now().strftime("%y%m%d") + registration_number
    return number
    # if len(OwnedVehicle.objects.filter(release_number=number)) > 0:
    #     return generate_release_number
    # else:
    #     return number


def check_invalid_product_params(params: list[dict]):
    for param in params:
        filtered_dict = {k: v for k, v in param.items() if not v <= 0}
        if len(filtered_dict) == 0:
            print("check_invalid_product_params")
            print(filtered_dict)
            return False
    return True