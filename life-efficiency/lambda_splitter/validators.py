import json
import logging
from dataclasses import dataclass
from datetime import datetime

from helpers.datetime import string_to_datetime
from lambda_splitter.errors import HTTPAwareException


class Validator:

    def validate(self, event: dict) -> dict:
        raise NotImplementedError()


@dataclass
class TypedField:
    name: str
    type: type = str


class FieldValidator(Validator):

    def __init__(self, required_fields: list[TypedField or str], optional_fields: list[TypedField or str] = None):
        if optional_fields is None:
            optional_fields = []
        self.required_fields = [TypedField(x) if isinstance(x, str) else x for x in required_fields]
        self.optional_fields = [TypedField(x) if isinstance(x, str) else x for x in optional_fields]

    def get_fields(self, event: dict) -> dict:
        raise NotImplementedError

    def get_field_type(self) -> str:
        raise NotImplementedError

    def validate_type(self, field_name: str, field_value, expected_type: type):
        raise NotImplementedError

    def validate(self, event: dict) -> dict:
        fields = self.get_fields(event)
        present_field_names = set(fields.keys())
        required_field_names = set([x.name for x in self.required_fields])
        optional_field_names = set([x.name for x in self.optional_fields])
        field_mappings = {x.name: x.type for x in self.required_fields + self.optional_fields}
        missing_required_fields = required_field_names - present_field_names
        missing_optional_fields = optional_field_names - present_field_names
        additional_fields = {}

        if len(missing_required_fields) > 0:
            missing_field = list(missing_required_fields)[0]
            logging.info(f"Validation of field {missing_field} failed, field is missing")
            raise HTTPAwareException(400, f"{self.get_field_type()} `{missing_field}` is required")

        for field, field_value in fields.items():
            if field not in field_mappings.keys():
                logging.info(f"Validation of field {field} failed, field is not valid for this endpoint")
                raise HTTPAwareException(400, f"{self.get_field_type()} `{field}` is not supported")
            if field_mappings[field] == datetime:
                field_value = string_to_datetime(field_value)
            self.validate_type(field, field_value, field_mappings[field])
            if field_mappings[field] == int:
                field_value = int(field_value)
            additional_fields[field] = field_value

        for missing_optional_field in missing_optional_fields:
            additional_fields[missing_optional_field] = None

        return additional_fields


class JsonBodyValidator(FieldValidator):

    def get_fields(self, event: dict) -> dict:
        return json.loads(event['body'])

    def get_field_type(self) -> str:
        return "field"

    def validate_type(self, field_name: str, field_value, expected_type: type):
        if not isinstance(field_value, expected_type):
            logging.info(f"Validation of field {field_name} failed, field is wrong type")
            raise HTTPAwareException(400, f"{self.get_field_type()} `{field_name}` "
                                          f"must be of type {expected_type.__name__}")


class QueryParamValidator(FieldValidator):

    def get_fields(self, event: dict) -> dict:
        return event['queryStringParameters'] or {}

    def get_field_type(self) -> str:
        return "param"

    def validate_type(self, field_name: str, field_value, expected_type: type):
        pass
