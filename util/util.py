from enum import Enum

import orjson
from ninja.parser import Parser
from ninja.renderers import BaseRenderer


class ORJSONParser(Parser):
    def parse_body(self, request):
        print(request.body)
        # print(request)
        return orjson.loads(request.body)  # request.body 2 json


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.name
