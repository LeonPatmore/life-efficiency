import json
from typing import Any


class ResponseHandler:

    def handle(self, obj: Any):
        raise NotImplementedError


class JsonResponseHandler(ResponseHandler):

    def handle(self, obj: Any):
        return {
            'statusCode': 200,
            'body': json.dumps(obj, default=self.get_object_as_json)
        }

    @staticmethod
    def get_object_as_json(obj):
        if hasattr(obj, "to_json"):
            return obj.to_json()
        else:
            return vars(obj)
