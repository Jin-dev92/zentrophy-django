import datetime

import jwt

from conf.custom_exception import WrongTokenException
from conf.settings import SECRET_KEY, JWT_ENCRYPTION_ALG


def is_admin(user):  # 어드민 유저만 허용
    return user.is_staff and user.is_active


def is_valid_token(token: str):
    if len(token) != 36:
        raise WrongTokenException
    split = token.split(sep='-', maxsplit=4)
    if len(split[0]) != 8 or len(split[1]) != 4 or len(split[2]) != 4 or len(split[3]) != 4 or len(split[4]) != 12:
        raise WrongTokenException
    return token


def get_jwt_token(user_id: int):
    payload = {
        'id': user_id,
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.now()
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=JWT_ENCRYPTION_ALG)
    return {"token": token}