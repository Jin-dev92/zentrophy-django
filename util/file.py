import base64
import io
import os
from PIL import Image


def base64_decode(file: str):
    image_data = base64.b64decode(file)
    data_bytes_io = io.BytesIO(image_data)
    image = Image.open(data_bytes_io)
    return image


def delete_file(file):
    if os.path.isfile(file.path):  # 해당 경로에 파일이 있다면
        os.remove(file.path)
