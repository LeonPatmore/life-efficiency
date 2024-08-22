import enum
import json
from typing import Any


class ResponseHandler:

    def handle(self, obj: Any):
        raise NotImplementedError


class BasicResponseHandler(ResponseHandler):

    def __init__(self, code: int):
        self.code = code

    def handle(self, body: str):
        return {
            'statusCode': self.code,
        } | ({'body': body if body else {}})


class JsonResponseHandler(BasicResponseHandler):

    def __init__(self):
        super().__init__(200)

    def handle(self, obj: Any):
        return super().handle(json.dumps(obj, default=self.get_object_as_json))

    @staticmethod
    def get_object_as_json(obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        if hasattr(obj, "to_json"):
            return obj.to_json()
        else:
            return vars(obj)
