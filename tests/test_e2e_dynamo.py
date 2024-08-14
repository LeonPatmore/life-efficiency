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
def setup_dynamo_mock(request):
    boto3_mock = Mock()
    sys.modules['boto3'] = boto3_mock

    dynamodb_mock = Mock()
    boto3_mock.resource.return_value = dynamodb_mock

    table_init_config = request.param if hasattr(request, "param") else {}
    dynamodb_mock.Table.side_effect = lambda table_name: DynamoDbMock(table_init_config.get(table_name, []))


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


@pytest.mark.parametrize('setup_dynamo_mock',
                         [{"life-efficiency_local_todo-sets": [{"id": "abc123", "name": "set_one"}]}],
                         indirect=True)
def test_todo_sets(setup_dynamo_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "sets"
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == "abc123"
    assert res_json[0]["name"] == "set_one"


@pytest.mark.parametrize('setup_dynamo_mock',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 2, "Desc": "something else", "SetId": "setOne"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_day(setup_dynamo_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'day': 1
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 1


@pytest.mark.parametrize('setup_dynamo_mock',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 1, "Desc": "something else", "SetId": "setTwo"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_set_id(setup_dynamo_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'set_id': "setTwo"
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 2


@pytest.mark.parametrize('setup_dynamo_mock',
                         [{
                             "life-efficiency_local_weekly-todos": [
                                 {"id": "1", "Day": 1, "Desc": "something", "SetId": "setOne"},
                                 {"id": "2", "Day": 2, "Desc": "something else", "SetId": "setOne"},
                                 {"id": "3", "Day": 1, "Desc": "something else", "SetId": "setTwo"},
                                 {"id": "4", "Day": 2, "Desc": "something else", "SetId": "setTwo"},
                             ]
                         }],
                         indirect=True)
def test_weekly_todos_by_set_id_and_day(setup_dynamo_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        'queryStringParameters': {
            'set_id': "setTwo",
            'day': 1
        }
    }, {})
    assert 200 == res["statusCode"]
    res_json = json.loads(res["body"])
    assert len(res_json) == 1

    assert res_json[0]["id"] == 3
