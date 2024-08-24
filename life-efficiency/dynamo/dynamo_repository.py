import enum
import re
import uuid
from datetime import datetime
from decimal import Decimal

from helpers.datetime import datetime_to_string, string_to_datetime
from repository.repository import RepositoryImplementation

table_generator: callable = None


def dynamo_item(table_name: str, custom_dynamo_to_attribute_map: dict[str, str] = None):
    def dynamo_item_dec(cls):
        cls.table_name = table_name
        cls.custom_dynamo_to_attribute_map = {} if custom_dynamo_to_attribute_map is None \
            else custom_dynamo_to_attribute_map
        return cls

    return dynamo_item_dec


def _get_table(name: str):
    if table_generator is None:
        raise NotImplementedError("`table_generator` needs to be set before you can use this repository")
    # noinspection PyCallingNonCallable
    return table_generator(name)


class DynamoRepository(RepositoryImplementation):

    # noinspection PyUnresolvedReferences
    def __init__(self, object_type: type):
        super().__init__(object_type)
        self.table = _get_table(object_type.table_name)
        self.object_type = object_type
        self.custom_dynamo_to_attribute_map = object_type.custom_dynamo_to_attribute_map
        self.custom_attribute_to_dynamo_map = {v: k for k, v in self.custom_dynamo_to_attribute_map.items()}

    def _attribute_to_dynamo_key(self, attribute: str) -> str:
        if attribute == "id":
            return "id"
        if attribute in self.custom_attribute_to_dynamo_map:
            return self.custom_attribute_to_dynamo_map[attribute]
        return attribute.replace("_", " ").title().replace(" ", "")

    def _dynamo_key_to_attribute(self, key: str) -> str:
        if key in self.custom_dynamo_to_attribute_map:
            return self.custom_dynamo_to_attribute_map[key]
        return re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()

    @staticmethod
    def _object_to_dynamo_value(obj):
        if obj is None:
            return None
        if isinstance(obj, datetime):
            return datetime_to_string(obj)
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, float):
            return Decimal(str(obj))
        return obj

    @staticmethod
    def _dynamo_value_to_object(val, target_type: type):
        if val is None:
            return None
        if target_type == datetime:
            if val == "":
                return None
            return string_to_datetime(val)
        if target_type == int:
            return int(float(val))
        if target_type == float:
            return float(val)
        if issubclass(target_type, enum.Enum):
            return target_type[val]
        return val

    def _get_key_value_from_dynamo_pair(self, key: str, value) -> tuple:
        attribute = self._dynamo_key_to_attribute(key)
        value_type = vars(self.object_type)["__annotations__"][attribute]
        final_value = self._dynamo_value_to_object(value, value_type)
        return attribute, final_value

    # noinspection PyTypeChecker
    def _dynamo_to_obj(self, dynamo_keys: dict):
        return self.object_type(**dict(self._get_key_value_from_dynamo_pair(key, value)
                                       for key, value in dynamo_keys.items()))

    def add(self, item):
        if getattr(item, "id") is None:
            item = type(item)(**vars(item) | {"id": str(uuid.uuid4())})
        self.table.put_item(Item={self._attribute_to_dynamo_key(key): self._object_to_dynamo_value(value)
                                  for key, value in vars(item).items()})
        return item

    def get_all(self) -> list:
        return [self._dynamo_to_obj(x) for x in self.table.scan()["Items"]]

    def get(self, item_id: str):
        res = self.table.get_item(Key={'id': item_id})
        if res is not None and "Item" in res:
            return self._dynamo_to_obj(res["Item"])
        else:
            return None

    def remove(self, item_id: str):
        self.table.delete_item(Key={"id": item_id})

    def update(self, item_id: str, attribute: str, val):
        dynamo_key = self._attribute_to_dynamo_key(attribute)
        self.table.update_item(Key={"id": item_id},
                               ConditionExpression='attribute_exists(id)',
                               UpdateExpression=f"set {dynamo_key}=:a",
                               ExpressionAttributeValues={":a": self._object_to_dynamo_value(val)})
