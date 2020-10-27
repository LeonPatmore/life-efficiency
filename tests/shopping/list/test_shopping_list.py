from datetime import datetime

import pytest

from shopping.list.shopping_list import ShoppingList


class TestShoppingList(ShoppingList):

    def add_item(self, item: str, quantity: int, date_added: datetime):
        pass

    def remove_item(self, item: str, quantity: int):
        pass

    def get_items(self):
        return ['item-1', 'item-1', 'item-2', 'item-1']


@pytest.fixture
def setup_test_shopping_list():
    return TestShoppingList()


_setup_test_shopping_list = setup_test_shopping_list


def test_get_item_count(_setup_test_shopping_list):
    test_shopping_list = _setup_test_shopping_list
    count = test_shopping_list.get_item_count('item-1')
    assert count == 3
