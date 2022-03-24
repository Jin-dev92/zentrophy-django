import os
from typing import List
from django.db.models import Model
from ninja import UploadedFile

from conf import settings


def is_exist_file_in_model(obj: dict[UploadedFile], model: Model):
    # if len(queryset.filter(obj) == 0):
    #     return False
    return True


def delete_files(file_list: List[str]):
    if file_list is None:
        return True
    try:
        for file in file_list:
            os.remove(os.path.join(settings.MEDIA_ROOT, file))
    except Exception as e:
        raise Exception(e)
