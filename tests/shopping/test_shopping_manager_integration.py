from datetime import datetime, timedelta

import pytest

from helpers.datetime import get_current_datetime_utc
from repository import repository
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.list.shopping_list import ShoppingList
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems, RepeatingItem
from shopping.shopping_manager import ShoppingManager, UnexpectedBuyException
from tests.test_helpers import InMemoryRepository

CURRENT_TIME = datetime(2001, 1, 1, 1, 1, 1, 1)
TEST_ITEM = "test-item"
TEST_ITEM_2 = "test-item-2"


@pytest.fixture
def setup_shopping_manager(request):
    repository.repository_implementation = InMemoryRepository
    if not hasattr(request, 'param'):
        purchases = None
        repeating_items = None
        shopping_list = None
    else:
        purchases, repeating_items, shopping_list = request.param

    if purchases is None:
        purchases = []
    if repeating_items is None:
        repeating_items = []
    if shopping_list is None:
        shopping_list = []

    shopping_history = ShoppingHistory()
    for purchase in purchases:
        shopping_history.add(purchase)
    test_shopping_list = ShoppingList(get_current_datetime_utc)
    for item in shopping_list:
        test_shopping_list.increase_quantity(item, 1)
    repeating_items_obj = RepeatingItems()
    for repeating_item in repeating_items:
        repeating_items_obj.add(RepeatingItem(repeating_item))

    shopping_manager = ShoppingManager(shopping_history,
                                       test_shopping_list,
                                       repeating_items_obj,
                                       lambda: CURRENT_TIME + timedelta(days=1))

    return shopping_manager, test_shopping_list, shopping_history


def test_today_items_no_items_is_empty_list(setup_shopping_manager):
    shopping_manager, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == []


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           None)],
                         indirect=True)
def test_today_items_with_repeating_items(setup_shopping_manager):
    shopping_manager, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == [TEST_ITEM]


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [TEST_ITEM_2])],
                         indirect=True)
def test_today_items_multiple_items(setup_shopping_manager):
    shopping_manager, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == [TEST_ITEM, TEST_ITEM_2]


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_shopping_list_is_most_important(setup_shopping_manager):
    shopping_manager, shopping_list, _ = setup_shopping_manager

    shopping_manager.today_items()

    shopping_manager.complete_item(TEST_ITEM, 1)

    assert shopping_manager.today_items() == []
    assert TEST_ITEM not in shopping_list.get_all()


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_extra_items_are_used(setup_shopping_manager):
    shopping_manager, shopping_list, _ = setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 2)

    assert shopping_manager.today_items() == []
    assert TEST_ITEM not in shopping_list.get_all()


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_repeating_item(setup_shopping_manager):
    shopping_manager, shopping_list, _ = setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 6)

    assert shopping_manager.today_items() == []
    assert TEST_ITEM not in shopping_list.get_all()


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_not_repeating_item(setup_shopping_manager):
    shopping_manager, shopping_list, _ = setup_shopping_manager

    with pytest.raises(UnexpectedBuyException):
        shopping_manager.complete_item(TEST_ITEM, 4)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           [])],
                         indirect=True)
def test_complete_today(setup_shopping_manager):
    shopping_manager, shopping_list, _ = setup_shopping_manager

    shopping_manager.complete_today()

    assert shopping_manager.today_items() == []


@pytest.mark.parametrize("setup_shopping_manager",
                         [([],
                           [' '],
                           [])],
                         indirect=True)
def test_complete_item(setup_shopping_manager):
    shopping_manager, _, shopping_history = setup_shopping_manager

    shopping_manager.complete_item(' ', 1)

    assert len(shopping_history.get_all()) == 0
