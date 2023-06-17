import json
import os
import sys
from unittest import mock
from unittest.mock import Mock

import pytest

from shopping.shopping_manager import ShoppingManager
from tests.google_spreadsheet_test_helpers import generate_worksheet_mock


@pytest.fixture
def setup_configuration_mock():
    get_mock = Mock()
    get_mock.first.return_value = "06/06/2023, 21:37:42"

    def mock_spreadsheets(title, *_, **__):
        if title == "todo":
            return generate_worksheet_mock([[],
                                            ["1", "some-todo-item", "done", "07/06/2023, 00:57:32"],
                                            ["2", "some-todo-item", "in_progress", "07/06/2032, 00:57:32"],
                                            ["3", "some-todo-item", "not_started", "07/06/2010, 00:57:32"]])
        else:
            return generate_worksheet_mock([[""], [""], [""], [""], [""], [""], [""], [""]], get_mock)

    spreadsheet_mock = Mock()
    spreadsheet_mock.worksheets.return_value = []
    spreadsheet_mock.add_worksheet.side_effect = mock_spreadsheets

    service_account_mock = Mock()
    service_account_mock.open_by_key.return_value = spreadsheet_mock

    gspread_mock = Mock()
    gspread_mock.service_account.return_value = service_account_mock

    boto3_mock = Mock()
    boto3_client_mock = Mock()
    boto3_client_mock.get_secret_value.return_value = {
        "SecretString": "MySecret"
    }
    boto3_mock.client.return_value = boto3_client_mock

    sys.modules['gspread'] = gspread_mock
    sys.modules['boto3'] = boto3_mock


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd"})
def test_shopping_configuration(setup_configuration_mock):
    import configuration

    assert isinstance(configuration.shopping_manager, ShoppingManager)


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd"})
def test_todo_list_with_filter_that_returns_empty(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        "queryStringParameters": {
            "status": "unknown"
        }
    }, {})

    assert 200 == res["statusCode"]
    assert "[]" == res["body"]


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd"})
def test_todo_list_with_filter(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        "queryStringParameters": {
            "status": "done"
        }
    }, {})

    assert 200 == res["statusCode"]
    assert """[{"id": 1, "desc": "some-todo-item", "status": "done", "date_added": "07/06/2023, 00:57:32"}]""" \
           == res["body"]


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd"})
def test_todo_list_with_sorting(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "list"
        },
        "queryStringParameters": {
            "sort": "true"
        }
    }, {})

    assert 200 == res["statusCode"]
    res_body = json.loads(res["body"])
    assert res_body[0]["id"] == 2
    assert res_body[1]["id"] == 1
    assert res_body[2]["id"] == 3
