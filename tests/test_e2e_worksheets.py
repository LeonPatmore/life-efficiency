import json
import os
import sys
from datetime import datetime
from unittest import mock
from unittest.mock import Mock

import pytest

from shopping.shopping_manager import ShoppingManager
from tests.google_spreadsheet_test_helpers import generate_worksheet_mock
from tests.test_helpers import cleanup_modules


@pytest.fixture(autouse=True)
def reset_configuration():
    cleanup_modules(["configuration", "spreadsheet.spreadsheet_client_loader"])
    yield
    cleanup_modules(["configuration", "spreadsheet.spreadsheet_client_loader"])


@pytest.fixture
def setup_configuration_mock():
    def mock_spreadsheets(title, *_, **__):
        if title == "todo":
            return generate_worksheet_mock([[],
                                            ["1", "some-todo-item", "done", "07/06/2023, 00:57:32"],
                                            ["2", "some-todo-item", "in_progress", "07/06/2032, 00:57:32"],
                                            ["3", "some-todo-item", "not_started", "07/06/2010, 00:57:32"]])
        elif title == "todo-weekly":
            return generate_worksheet_mock([["01/01/2001, 01:01:01"],
                                            [1, 2, 'some todo task', "done", "", "done"],
                                            [2, 5, 'some todo task', "done", "", "done"],
                                            [3, 5, 'some todo task', "done", "", "done"]],
                                           get_first="01/01/2001, 01:01:01")
        elif title == "RepeatingItems":
            return generate_worksheet_mock([["item-1"], ["item-2"], ["item-3"]])
        elif title == "History":
            return generate_worksheet_mock([['item-1', '1', '01/01/2001, 01:01:01'],
                                            ['item-1', '1', '02/01/2001, 01:01:01'],
                                            ['item-1', '1', '03/01/2001, 01:01:01'],
                                            ['item-2', '1', '01/01/2001, 01:01:01'],
                                            ['item-2', '1', '05/01/2001, 01:01:01'],
                                            ['item-2', '1', '01/02/2001, 01:01:01']])
        elif title == "goals-manager":
            return generate_worksheet_mock([["year", "2023"], ["quarter", "q1"], ["some-goal", "in_progress"]])
        else:
            return generate_worksheet_mock([[""], [""], [""], [""], [""], [""], [""], [""]], "06/06/2023, 21:37:42")

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


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
def test_shopping_configuration(setup_configuration_mock):
    import configuration

    assert isinstance(configuration.shopping_manager, ShoppingManager)


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
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


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
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
    assert """[{"id": 1, "desc": "some-todo-item", "status": "done", "date_added": "07/06/2023, 00:57:32", """ \
           + """"date_done": null}]""" == res["body"]


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
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


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
def test_todo_weekly_get_day(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        },
        "queryStringParameters": {
            "day": 5
        }
    }, {})

    assert 200 == res["statusCode"]
    res_body = json.loads(res["body"])
    assert len(res_body) == 2
    assert res_body[0]["desc"] == "some todo task"
    assert res_body[0]["day"] == 5
    assert res_body[0]["id"] == 2
    assert res_body[1]["desc"] == "some todo task"
    assert res_body[1]["day"] == 5
    assert res_body[1]["id"] == 3


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
def test_todo_weekly_get_all(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "todo",
            "subcommand": "weekly"
        }
    }, {})

    assert 200 == res["statusCode"]
    res_body = json.loads(res["body"])
    assert len(res_body) == 3


@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
def test_get_goals(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "goals",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]
    res_body = json.loads(res["body"])
    assert res_body == {
        "2023": {
            "q1": [{
                "name": "some-goal",
                "progress": "in_progress"
            }],
            "q2": [],
            "q3": [],
            "q4": []
        }
    }


@mock.patch('helpers.datetime.datetime')
@mock.patch.dict(os.environ, {"SPREADSHEET_KEY_SECRET_NAME": "asd",
                              "BACKEND": "worksheets"})
def test_get_repeating_details(datetime_mock, setup_configuration_mock):
    datetime_mock.datetime.now = Mock(return_value=datetime.strptime('Feb 10 2001', '%b %d %Y'))
    datetime_mock.datetime.strptime = lambda x, y: datetime.strptime(x, y)
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating-details"
        }
    }, {})

    assert 200 == res["statusCode"]
    res_body = json.loads(res["body"])
    assert res_body == {
        "item-1": {
            "avg_gap_days": 1,
            "time_since_last_bought": 37,
            "today": True
        },
        "item-2": {
            "avg_gap_days": 16,
            "time_since_last_bought": 8,
            "today": False
        },
        "item-3": {
            "avg_gap_days": None,
            "time_since_last_bought": None,
            "today": False
        }
    }
