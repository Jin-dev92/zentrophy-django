# from datetime import datetime

from ninja import Schema

# from order.schema import OrderListSchema
# from product.schema import VehicleListSchema
from product.schema import VehicleListSchema


class MemberInsertSchema(Schema):
    username: str = None
    email: str = None
    # password: str
    address: str = None
    address_detail: str = None
    member_info_number: str = None
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
    # is_created: datetime = None
    # is_updated: datetime = None


class AdminInsertSchema(Schema):
    username: str
    email: str
    password: str
    # address: str = None
    # address_detail: str = None
    # phone_number: str = None
    # zipCode: str = None
    # is_business: bool = None


class MemberOwnedVehiclesListSchema(Schema):
    id: int
    vehicle: VehicleListSchema = None
    license_code: str = None
    battery_left: int
