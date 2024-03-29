import base64
import os
from django.core.files.base import ContentFile

from conf.custom_exception import FormatNotSupportedException


def base64_decode(file):
    try:
        convert_str = file + '=' * (4 - len(file) % 4)
        format, imgstr = convert_str.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)  # You can save this as file instance.
        return data
    except Exception:
        raise FormatNotSupportedException


def delete_file(file):
    if os.path.isfile(file):  # 해당 경로에 파일이 있다면
        os.remove(file)
