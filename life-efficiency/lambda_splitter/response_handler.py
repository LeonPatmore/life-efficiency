import enum
import json
from datetime import datetime, timedelta
from typing import Any

from helpers.datetime import datetime_to_string


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
            return obj.name.lower()
        if isinstance(obj, datetime):
            return datetime_to_string(obj)
        if hasattr(obj, "to_json"):
            return obj.to_json()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, timedelta):
            return str(obj)
        else:
            return vars(obj)
