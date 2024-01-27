import os
import sys
from unittest import mock
from unittest.mock import Mock

import pytest

from shopping.shopping_manager import ShoppingManager
from tests.google_spreadsheet_test_helpers import generate_worksheet_mock


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

    # boto3_mock = Mock()
    # boto3_client_mock = Mock()
    # boto3_client_mock.get_secret_value.return_value = {
    #     "SecretString": "MySecret"
    # }
    # boto3_mock.client.return_value = boto3_client_mock
    #
    # sys.modules['gspread'] = gspread_mock
    # sys.modules['boto3'] = boto3_mock


@mock.patch.dict(os.environ, {"BACKEND": "dynamo", "AWS_DEFAULT_REGION": "eu-west-1"})
def test_shopping_configuration(setup_configuration_mock):
    import configuration

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]

