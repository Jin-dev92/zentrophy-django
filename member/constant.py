from enum import Enum


# class CardCompany(models.TextChoices):
#     BC = 'bc'
#     KB = 'kb'
#     SAMSUNG = 'samsung'
#     SHINHAN = 'shinhan'
#     UURI = 'uuri'
#     HANA = 'hana'
#     LOTTE = 'lotte'
#     HYUNDAI = 'hyundai'
#     NH = 'nh'
#     ETC = 'etc'


class MemberSort(Enum):
    RECENT = 'recent'
    LATER = 'later'
