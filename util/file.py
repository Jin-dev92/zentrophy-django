import base64
import io
import os
from typing import List, Optional

from PIL import Image
from ninja import UploadedFile, File
from conf import settings


def delete_files(file_list: Optional[List[UploadedFile]]):
    if file_list is None:
        return True
    try:
        for file in file_list:
            os.remove(os.path.join(settings.MEDIA_ROOT, file))
    except Exception as e:
        raise Exception('delete_files exception')


def base64_decode(file: str):
    image_data = base64.b64decode(file)
    data_bytes_io = io.BytesIO(image_data)
    image = Image.open(data_bytes_io)
    return image
