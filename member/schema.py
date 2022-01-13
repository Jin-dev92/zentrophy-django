# from datetime import date
from ninja import Schema


class MemberIn(Schema):
    user_name: str
    user_mail: str
    phone_number: str
    address: str


class MemberOut(Schema):
    id: int
    user_name: str
    user_mail: str
    phone_number: str
    address: str
