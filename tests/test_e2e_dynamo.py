import json
import sys
import uuid
from unittest.mock import Mock

import pytest

from tests.dynamo_db_mock import DynamoDbMock
from tests.test_helpers import cleanup_modules


@pytest.fixture(autouse=True)
def reset_configuration():
    cleanup_modules(["configuration"])
    yield
    cleanup_modules(["configuration"])


@pytest.fixture
def setup_dynamo_mock():
    boto3_mock = Mock()
    sys.modules['boto3'] = boto3_mock

    dynamodb_mock = Mock()
    boto3_mock.resource.return_value = dynamodb_mock

    dynamodb_mock.Table.side_effect = lambda x: DynamoDbMock()


def test_shopping_list_adding_items_together(setup_dynamo_mock):
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})
    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    item_part = [x for x in body["items"] if x["name"] == item_name][0]
    assert item_part["name"] == item_name
    assert item_part["quantity"] == 6


def test_repeating_items(setup_dynamo_mock):
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        },
        "body": f"""{{"item": "{item_name}"}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        }
    }, {})

    assert 200 == res["statusCode"]
    assert item_name in json.loads(res["body"])["items"]


def test_todo(setup_dynamo_mock):
    import configuration

    def _todo_item_exists(todo_id: str) -> bool:
        todos = json.loads(configuration.handler({
            'httpMethod': "GET",
            'pathParameters': {
                "command": "todo",
                "subcommand": "list"
            }
        }, {})["body"])
        return len(list(filter(lambda x: x["id"] == todo_id, todos))) > 0

    res = configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        'body': json.dumps({
            "desc": "a test todo"
        })
    }, {})
    assert 200 == res["statusCode"]
    todo_id = json.loads(res["body"])["id"]

    res = configuration.handler({
        'httpMethod': "PATCH",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        'body': json.dumps({
            "id": todo_id,
            "status": "done"
        })
    }, {})
    assert 200 == res["statusCode"]

    assert _todo_item_exists(todo_id)

    res = configuration.handler({
        'httpMethod': "DELETE",
        'pathParameters': {
            "command": "todo",
            "subcommand": f"list/{todo_id}"
        },
        'path': f"todo/list/{todo_id}"
    }, {})
    assert 200 == res["statusCode"]

    assert not _todo_item_exists(todo_id)
