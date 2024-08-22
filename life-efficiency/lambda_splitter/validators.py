import json
from dataclasses import dataclass

from lambda_splitter.errors import HTTPAwareException


class Validator:

    def validate(self, event: dict):
        raise NotImplementedError()


@dataclass
class RequiredField:
    name: str
    type: type = str


class RequiredFieldValidator(Validator):

    def __init__(self, required_fields: list[RequiredField or str]):
        self.required_fields = [RequiredField(x) if isinstance(x, str) else x for x in required_fields]

    def get_fields(self, event: dict) -> dict:
        raise NotImplementedError

    def get_field_type(self) -> str:
        raise NotImplementedError

    def validate(self, event: dict):
        fields = self.get_fields(event)
        for required_field in self.required_fields:
            if required_field.name not in fields:
                raise HTTPAwareException(400, f"{self.get_field_type()} `{required_field.name}` is required")
            field = fields[required_field.name]
            if type(field) is not required_field.type:
                raise HTTPAwareException(400, f"{self.get_field_type()} `{required_field.name}` "
                                              f"must be of type {required_field.type.__name__}")


class JsonBodyValidator(RequiredFieldValidator):

    def get_fields(self, event: dict) -> dict:
        return json.loads(event['body'])

    def get_field_type(self) -> str:
        return "field"


class QueryParamValidator(RequiredFieldValidator):

    def get_fields(self, event: dict) -> dict:
        return event['queryStringParameters'] or {}

    def get_field_type(self) -> str:
        return "param"
