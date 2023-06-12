import json
from typing import Any


class ResponseHandler:

    def handle(self, obj: Any):
        raise NotImplementedError


class JsonResponseHandler(ResponseHandler):

    def handle(self, obj: Any):
        return {
            'statusCode': 200,
            'body': json.dumps(obj)
        }
