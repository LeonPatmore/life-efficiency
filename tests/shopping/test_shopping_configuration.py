import sys
from unittest.mock import Mock

import pytest

from shopping.shopping_manager import ShoppingManager


@pytest.fixture
def setup_configuration_mock():
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = [[]]
    spreadsheet_mock = Mock()
    spreadsheet_mock.worksheets.return_value = []
    spreadsheet_mock.add_worksheet.return_value = worksheet_mock
    configuration_mock = Mock(spreadsheet=spreadsheet_mock)
    configuration_mock.spreadsheet.return_value = spreadsheet_mock
    sys.modules['configuration'] = configuration_mock


_setup_configuration_mock = setup_configuration_mock


def test_shopping_configuration(_setup_configuration_mock):
    from shopping import shopping_configuration

    assert isinstance(shopping_configuration.shopping_manager, ShoppingManager)
