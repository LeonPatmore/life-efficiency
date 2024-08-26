from unittest.mock import Mock

import pytest

from helpers.datetime import get_current_datetime_utc
from shopping.list.shopping_list import ShoppingList, ShoppingListItem


@pytest.fixture(scope="session")
def setup_test_shopping_list() -> ShoppingList:
    mocked_shopping_list = ShoppingList(get_current_datetime_utc)
    mocked_shopping_list.get = Mock()
    mocked_shopping_list.add = Mock()
    mocked_shopping_list.remove = Mock()
    mocked_shopping_list.set_item_quantity = Mock()
    return mocked_shopping_list


def test_get_item_count_when_get_returns_item_return_quantity(setup_test_shopping_list):
    mocked_shopping_list = setup_test_shopping_list
    mocked_shopping_list.get.return_value = ShoppingListItem("item-1", 5, get_current_datetime_utc())
    count = mocked_shopping_list.get_item_count('item-1')
    assert count == 5


def test_get_item_count_when_get_returns_none_return_0(setup_test_shopping_list):
    mocked_shopping_list = setup_test_shopping_list
    mocked_shopping_list.get.return_value = None
    count = mocked_shopping_list.get_item_count('item-1')
    assert count == 0


@pytest.mark.parametrize("amount_to_reduce", [2, 3])
def test_reduce_quantity_removes_item_if_quantity_is_over_or_equal_current_quantity(setup_test_shopping_list,
                                                                                    amount_to_reduce):
    mocked_shopping_list = setup_test_shopping_list
    setup_test_shopping_list.get.return_value = ShoppingListItem("item-1", 2, get_current_datetime_utc())

    mocked_shopping_list.reduce_quantity("item-1", amount_to_reduce)

    # noinspection PyUnresolvedReferences
    mocked_shopping_list.remove.assert_called_with("item-1")


@pytest.mark.parametrize("amount_to_reduce", [1, 0])
def test_reduce_quantity_updates_item_if_quantity_is_smaller_than_current_quantity(setup_test_shopping_list,
                                                                                   amount_to_reduce):
    mocked_shopping_list = setup_test_shopping_list
    setup_test_shopping_list.get.return_value = ShoppingListItem("item-1", 2, get_current_datetime_utc())

    mocked_shopping_list.reduce_quantity("item-1", amount_to_reduce)

    # noinspection PyUnresolvedReferences
    mocked_shopping_list.set_item_quantity.assert_called_with("item-1", (2 - amount_to_reduce))


def test_increase_quantity_updates_item_if_item_already_exists(setup_test_shopping_list):
    mocked_shopping_list = setup_test_shopping_list
    setup_test_shopping_list.get.return_value = ShoppingListItem("item-1", 2, get_current_datetime_utc())

    mocked_shopping_list.increase_quantity("item-1", 2)

    # noinspection PyUnresolvedReferences
    mocked_shopping_list.set_item_quantity.assert_called_with("item-1", 4)


def test_increase_quantity_adds_item_if_item_does_not_exist(setup_test_shopping_list):
    mocked_shopping_list = setup_test_shopping_list
    setup_test_shopping_list.get.return_value = None

    mocked_shopping_list.increase_quantity("item-1", 2)

    # noinspection PyUnresolvedReferences
    mocked_shopping_list.add.assert_called_once()


def test_increase_quantity_ensures_that_item_is_lower_case(setup_test_shopping_list):
    mocked_shopping_list = setup_test_shopping_list
    setup_test_shopping_list.get.return_value = None

    mocked_shopping_list.increase_quantity("Item-1", 2)

    # noinspection PyUnresolvedReferences
    called_item = mocked_shopping_list.add.call_args.args[0]
    assert called_item.id == "item-1"
