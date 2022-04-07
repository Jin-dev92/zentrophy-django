import base64
import imghdr
import io
import os

from PIL import Image


# def is_base64_image():
#     pass


def base64_decode(file):
    image_data = base64.b64decode(file)
    extension_check = imghdr.what(None, h=image_data)  # 이미지인지 확장자를 통해 확인함. 아닐 시 error 뱉음.
    data_bytes_io = io.BytesIO(image_data)
    image = Image.open(data_bytes_io)
    return image


def delete_file(file):
    if os.path.isfile(file.path):  # 해당 경로에 파일이 있다면
        os.remove(file.path)
