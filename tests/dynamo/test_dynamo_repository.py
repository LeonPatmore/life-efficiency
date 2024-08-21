from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock

import pytest

from dynamo import dynamo_repository
from dynamo.dynamo_repository import DynamoRepository, dynamo_item


@pytest.fixture
def setup_table_generator():
    mock_func = Mock()
    table_mock = Mock()
    mock_func.return_value = table_mock
    dynamo_repository.table_generator = mock_func
    return mock_func, table_mock


@dynamo_item("test_table")
@dataclass
class TestObject:
    id: str
    str_field: str
    int_field: int
    datetime_field: datetime


class TestRepo(DynamoRepository):

    def __init__(self):
        super().__init__(TestObject)


def test_table_generator_is_called_with_table_name_from_decorator(setup_table_generator):
    mock_func, _ = setup_table_generator
    TestRepo()

    mock_func.assert_called_with("test_table")


def test_add_item(setup_table_generator):
    _, table_mock = setup_table_generator
    repo = TestRepo()

    repo.add(TestObject("id", "my string", 101, datetime(1, 1, 1, 1, 1, 1)))

    table_mock.put_item.assert_called_with(Item={"id": "id",
                                                 "StrField": "my string",
                                                 "IntField": 101,
                                                 "DatetimeField": "01/01/0001, 01:01:01"})


def test_get_all(setup_table_generator):
    _, table_mock = setup_table_generator
    table_mock.scan.return_value = {
        "Items": [
            {
                "id": "some-id",
                "StrField": "my string",
                "IntField": 101,
                "DatetimeField": "01/01/0001, 01:01:01"
            }
        ]
    }
    repo = TestRepo()

    results = repo.get_all()

    assert len(results) == 1
    item = results[0]
    assert isinstance(item, TestObject)
    assert item.id == "some-id"
    assert item.str_field == "my string"
    assert item.int_field == 101
    assert item.datetime_field == datetime(1, 1, 1, 1, 1, 1)
