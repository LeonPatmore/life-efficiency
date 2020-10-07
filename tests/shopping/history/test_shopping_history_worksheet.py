from datetime import datetime
from unittest.mock import Mock

import pytest

from shopping.history.shopping_history_worksheet import ShoppingHistoryWorksheet
from shopping.history.shopping_item_purchase import ShoppingItemPurchase


VALID_ROW = ['some-item', '2', '01/01/2001, 01:01:01']


def _validate_valid_row_shopping_item_purchase(the_purchase: ShoppingItemPurchase):
    assert the_purchase.item == "SOME-ITEM"
    assert the_purchase.quantity == 2
    assert the_purchase.purchase_datetime == datetime(2001, 1, 1, 1, 1, 1, 0)


@pytest.fixture
def setup_shopping_history_worksheet_with_values(request):
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param
    return ShoppingHistoryWorksheet(worksheet_mock)


_setup_shopping_history_worksheet_with_values = setup_shopping_history_worksheet_with_values


@pytest.fixture
def setup_shopping_history_worksheet_with_insert_mock():
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = [[]]
    return worksheet_mock, ShoppingHistoryWorksheet(worksheet_mock)


_setup_shopping_history_worksheet_with_insert_mock = setup_shopping_history_worksheet_with_insert_mock


@pytest.mark.parametrize('_setup_shopping_history_worksheet_with_values', [[[]]], indirect=True)
def test_load_all_purchases_empty(_setup_shopping_history_worksheet_with_values):
    shopping_history_worksheet = _setup_shopping_history_worksheet_with_values

    all_purchases = shopping_history_worksheet.get_all_purchases()

    assert len(all_purchases) == 0


@pytest.mark.parametrize('_setup_shopping_history_worksheet_with_values',
                         [[VALID_ROW]],
                         indirect=True)
def test_load_all_purchases_not_empty(_setup_shopping_history_worksheet_with_values):
    shopping_history_worksheet = _setup_shopping_history_worksheet_with_values

    all_purchases = shopping_history_worksheet.get_all_purchases()

    assert len(all_purchases) == 1
    assert isinstance(all_purchases[0], ShoppingItemPurchase)
    the_purchase = all_purchases[0]
    _validate_valid_row_shopping_item_purchase(the_purchase)


@pytest.mark.parametrize('_setup_shopping_history_worksheet_with_values',
                         [[['some-item', '2', '01/01/2001, 01:01:01'], ['invalid-row']]],
                         indirect=True)
def test_load_all_purchases_when_invalid_row_ignore(_setup_shopping_history_worksheet_with_values):
    shopping_history_worksheet = _setup_shopping_history_worksheet_with_values

    all_purchases = shopping_history_worksheet.get_all_purchases()

    assert len(all_purchases) == 1
    assert isinstance(all_purchases[0], ShoppingItemPurchase)
    the_purchase = all_purchases[0]
    _validate_valid_row_shopping_item_purchase(the_purchase)


def test_add_purchase(_setup_shopping_history_worksheet_with_insert_mock):
    worksheet_mock, shopping_history_worksheet = _setup_shopping_history_worksheet_with_insert_mock

    shopping_history_worksheet.add_purchase(ShoppingItemPurchase('some-item', 1, datetime(2001, 1, 1, 1, 1, 1, 0)))

    worksheet_mock.insert_row.assert_called_once_with(['SOME-ITEM', 1, '01/01/2001, 01:01:01'], 1)
