from datetime import datetime
from unittest.mock import Mock

import pytest

from shopping.list.shopping_list_worksheet import ShoppingListWorksheet


@pytest.fixture
def setup_shopping_list_worksheet(request):
    if not hasattr(request, 'param'):
        setattr(request, 'param', [[]])
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param

    shopping_list_worksheet = ShoppingListWorksheet(worksheet_mock)

    return worksheet_mock, shopping_list_worksheet


_setup_shopping_list_worksheet = setup_shopping_list_worksheet


def test_get_items_no_items(_setup_shopping_list_worksheet):
    _, shopping_list_worksheet = _setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert items == []


@pytest.mark.parametrize("_setup_shopping_list_worksheet", [[["item-1", "2"], ["item-2", "3"]]], indirect=True)
def test_get_items_with_items(_setup_shopping_list_worksheet):
    _, shopping_list_worksheet = _setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert items == ["item-1", "item-1", "item-2", "item-2", "item-2"]


@pytest.mark.parametrize("_setup_shopping_list_worksheet", [[["item-1", "2"], ["item-2", "not-int"]]], indirect=True)
def test_get_items_with_unparseable_row(_setup_shopping_list_worksheet):
    _, shopping_list_worksheet = _setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert items == ["item-1", "item-1"]


def test_add_item(_setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = _setup_shopping_list_worksheet
    shopping_list_worksheet.add_item("item", 5, datetime(2001, 1, 1, 1, 1, 1, 1))
    worksheet_mock.insert_row.assert_called_with(["item", "5", "01/01/2001, 01:01:01"], 1)
