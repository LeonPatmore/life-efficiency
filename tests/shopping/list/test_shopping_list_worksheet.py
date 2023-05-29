from datetime import datetime
from unittest.mock import Mock, call

import pytest

from shopping.list.shopping_list import ShoppingListItem
from shopping.list.shopping_list_worksheet import ShoppingListWorksheet, NotEnoughItemsInList


@pytest.fixture
def setup_shopping_list_worksheet(request):
    if not hasattr(request, 'param'):
        setattr(request, 'param', [[]])
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param

    shopping_list_worksheet = ShoppingListWorksheet(worksheet_mock, lambda: datetime(2001, 1, 1, 1, 1, 1, 1))

    return worksheet_mock, shopping_list_worksheet


def test_get_items_no_items(setup_shopping_list_worksheet):
    _, shopping_list_worksheet = setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert items == []


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item-1", "2", "29/05/2023, 11:09:16"],
                           ["item-2", "3", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_get_items_with_items(setup_shopping_list_worksheet):
    _, shopping_list_worksheet = setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert 2 == len(items)
    assert items[0].name == "item-1"
    assert items[0].quantity == 2
    assert items[0].date_added == datetime(2023, 5, 29, 11, 9, 16)
    assert items[1].name == "item-2"
    assert items[1].quantity == 3
    assert items[1].date_added == datetime(2023, 5, 29, 11, 9, 16)


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item-1", "2", "29/05/2023, 11:09:16"],
                           ["item-2", "not-int", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_get_items_with_unparseable_row(setup_shopping_list_worksheet):
    _, shopping_list_worksheet = setup_shopping_list_worksheet
    items = shopping_list_worksheet.get_items()
    assert 1 == len(items)
    assert items[0].name == "item-1"


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item-1", "2", "29/05/2023, 11:09:16"],
                           ["item-1", "3", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_get_item_count_multiple_rows(setup_shopping_list_worksheet):
    _, shopping_list_worksheet = setup_shopping_list_worksheet
    assert 5 == shopping_list_worksheet.get_item_count("item-1")


def test_increase_quantity_when_new_item(setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = setup_shopping_list_worksheet
    shopping_list_worksheet.increase_quantity("item", 5)
    worksheet_mock.insert_row.assert_called_with(["item", "5", "01/01/2001, 01:01:01"], 1)


@pytest.mark.parametrize("setup_shopping_list_worksheet", [[["item", "2", "29/05/2023, 11:09:16"]]], indirect=True)
def test_reduce_quantity_no_item(setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = setup_shopping_list_worksheet
    shopping_list_worksheet.reduce_quantity("item", 0)
    worksheet_mock.update_cell.assert_not_called()
    worksheet_mock.delete_row.assert_not_called()


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item", "2", "29/05/2023, 11:09:16"],
                           ["item", "2", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_reduce_quantity_when_multiple_rows(setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = setup_shopping_list_worksheet
    shopping_list_worksheet.reduce_quantity("item", 3)
    worksheet_mock.update_cell.assert_called_once_with(1, 2, "1")
    worksheet_mock.delete_rows.assert_called_once_with(2)


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item", "2", "29/05/2023, 11:09:16"],
                           ["item", "2", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_reduce_quantity_when_multiple_rows_but_only_one_required(setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = setup_shopping_list_worksheet
    shopping_list_worksheet.reduce_quantity("item", 2)
    worksheet_mock.update_cell.assert_not_called()
    worksheet_mock.delete_rows.assert_called_once_with(2)


@pytest.mark.parametrize("setup_shopping_list_worksheet",
                         [[["item", "2", "29/05/2023, 11:09:16"],
                           ["item", "2", "29/05/2023, 11:09:16"]]],
                         indirect=True)
def test_reduce_quantity_not_enough_items_in_list_just_deletes_all_rows(setup_shopping_list_worksheet):
    worksheet_mock, shopping_list_worksheet = setup_shopping_list_worksheet
    shopping_list_worksheet.reduce_quantity("item", 5)
    worksheet_mock.delete_rows.assert_has_calls([call(2), call(1)])
