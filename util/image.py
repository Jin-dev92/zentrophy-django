import base64


def decode_image(data: str):
    image = base64.b64decode(data)
    # now = datetime.now()
    # now = datetime.timestamp(now)
    # file_name = f'{now}.jpg'
    # e = open(file_name, 'wb')
    # e.write(image)
    # e.close()
    return image
