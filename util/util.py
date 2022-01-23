import orjson
from django.db import models
from ninja.parser import Parser
from ninja.renderers import BaseRenderer


class TimeStampModel(models.Model):
    is_created = models.DateTimeField(auto_now_add=True)  # 처음에 추가될때 생성된다.
    is_updated = models.DateTimeField(auto_now=True)  # 처음 추가 될때 생성이 되면서 데이터가 바뀔때 마다 같이 바뀌게된다.

    class Meta:
        abstract = True


class ORJSONParser(Parser):
    def parse_body(self, request):
        print(request.body)
        # print(request)
        return orjson.loads(request.body)  # request.body 2 json


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)
