import os
import sys
from unittest import mock
from unittest.mock import Mock

import pytest

from shopping.shopping_manager import ShoppingManager


@pytest.fixture
def setup_configuration_mock():
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = [[""], [""], [""], [""], [""], [""], [""], [""]]
    get_mock = Mock()
    get_mock.first.return_value = "06/06/2023, 21:37:42"
    worksheet_mock.get.return_value = get_mock
    spreadsheet_mock = Mock()
    spreadsheet_mock.worksheets.return_value = []
    spreadsheet_mock.add_worksheet.return_value = worksheet_mock

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
