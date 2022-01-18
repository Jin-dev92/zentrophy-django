import orjson
from ninja.parser import Parser


class ORJSONParser(Parser):
    def parse_body(self, request):
        print(request.body)
        # print(request)
        return orjson.loads(request.body)  # request.body 2 json


