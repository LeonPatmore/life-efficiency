import pytest

from helpers.datetime import get_current_datetime_utc
from shopping.list.shopping_list import ShoppingList, ShoppingListItem


class TestShoppingList(ShoppingList):

    def get_items(self):
        return [ShoppingListItem("item-1", 2, get_current_datetime_utc()),
                ShoppingListItem("item-1", 1, get_current_datetime_utc()),
                ShoppingListItem("item-2", 3, get_current_datetime_utc())]


@pytest.fixture(scope="session")
def setup_test_shopping_list() -> TestShoppingList:
    return TestShoppingList(get_current_datetime_utc)


_setup_test_shopping_list = setup_test_shopping_list


def test_get_item_count(_setup_test_shopping_list):
    test_shopping_list = _setup_test_shopping_list
    count = test_shopping_list.get_item_count('item-1')
    assert count == 3


def test_get_item_count_when_no_item_returns_0(_setup_test_shopping_list):
    test_shopping_list = _setup_test_shopping_list
    count = test_shopping_list.get_item_count('item-3')
    assert count == 0


def test_get_item_counts_items(_setup_test_shopping_list):
    item = _setup_test_shopping_list.get_item("item-1")
    assert 3 == item.quantity
    assert "item-1" == item.name


def test_get_item_when_no_item_returns_none(_setup_test_shopping_list):
    assert _setup_test_shopping_list.get_item("item-does-not-exist") is None
