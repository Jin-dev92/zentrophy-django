import random
import string

from conf.settings import LICENSE_NUMBER_LENGTH
from history.models import AfterService

random_variation = string.digits + string.ascii_uppercase
# RANDOM_MAX_LENGTH = 16


def generate_random_number(length: int = LICENSE_NUMBER_LENGTH):  # 2. A/S 접수번호 - (랜덤생성, 16자리의 숫자 및 영문 대문자)
    global random_variation
    registration_number = "".join(random.choices(random_variation, k=length))  # 생성된 난수
    obj = AfterService.objects.filter(registration_number=registration_number).all()
    if len(obj) > 0:
        generate_random_number()
    else:
        return registration_number
