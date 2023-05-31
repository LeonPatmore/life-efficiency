import json

from lambda_splitter.errors import HTTPAwareException


class Validator:

    def validate(self, event: dict):
        raise NotImplementedError()


class JsonBodyValidator(Validator):

    def __init__(self, required_fields: list[str]):
        self.required_fields = required_fields

    def validate(self, event: dict):
        body = json.loads(event['body'])
        for required_field in self.required_fields:
            if required_field not in body:
                raise HTTPAwareException(400, f"field `{required_field}` is required")


class QueryParamValidator(Validator):

    def __init__(self, required_params: list[str]):
        self.required_params = required_params

    def validate(self, event: dict):
        params = event['queryStringParameters'] or []
        for required_param in self.required_params:
            if required_param not in params:
                raise HTTPAwareException(400, f"param `{required_param}` is required")
