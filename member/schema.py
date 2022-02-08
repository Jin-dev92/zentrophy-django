from datetime import datetime

from ninja import Schema


class MemberInsertSchema(Schema):
    username: str = None
    email: str = None
    # password: str
    address: str = None
    address_detail: str = None
    number: str = None
    zipCode: str = None
    is_business: bool = False


class MemberListSchema(Schema):
    id: int
    username: str
    email: str
    address: str
    address_detail: str
    member_info_number: str
    zipCode: str
    is_business: bool
    is_created: datetime
    is_updated: datetime


class AdminInsertSchema(Schema):
    username: str
    email: str
    password: str
    # address: str = None
    # address_detail: str = None
    # phone_number: str = None
    # zipCode: str = None
    # is_business: bool = None
