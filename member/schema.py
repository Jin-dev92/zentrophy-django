# from datetime import date
from ninja import Schema


class MemberInsertScheme(Schema):
    user_name: str
    user_mail: str
    phone_number: str
    address: str


class MemberListSchema(Schema):
    id: int
    user_name: str
    user_mail: str
    phone_number: str
    address: str


# class MemberModifySchema(Schema):
#     user_name: str
#     user_mail: str
#     phone_number: str
#     address: str
