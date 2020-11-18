import types
from datetime import datetime, timedelta
from enum import Enum

import pytest

from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.list.shopping_list import ShoppingList
from shopping.mealplan.meal_plan import MealPlan
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems
from shopping.shopping_manager import ShoppingManager, UnexpectedBuyException
from tests.shopping.mealplan.test_days import TestDays

CURRENT_TIME = datetime(2001, 1, 1, 1, 1, 1, 1)
TEST_ITEM = "test-item"
TEST_ITEM_2 = "test-item-2"
TEST_ITEM_3 = "test-item-3"


class TestMealPlan(MealPlan):

    def __init__(self, meal_plan, time_provider: types.FunctionType, days: Enum):
        self._meal_plan = meal_plan
        super().__init__(time_provider, days)
        self.meal_purchased = len(meal_plan) * [False]

    def _load_meal_plans(self):
        self.mean_plan = self._meal_plan

    def _get_purchase_time(self) -> datetime:
        return CURRENT_TIME

    def _reset_purchase_time(self, new_time: datetime):
        pass

    def _is_meal_purchased_implementation(self, day) -> bool:
        return self.meal_purchased[day.value]

    def _purchase_meal_implementation(self, day):
        self.meal_purchased[day.value] = True


class TestShoppingHistory(ShoppingHistory):

    def __init__(self, purchases: list):
        self.purchases = purchases
        super().__init__()

    def _load_all_purchases(self) -> list:
        return self.purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.purchases.append(purchase)


class TestShoppingList(ShoppingList):

    def __init__(self, shopping_list: list):
        self.shopping_list = shopping_list

    def get_items(self) -> list:
        return self.shopping_list

    def add_item(self, item: str, quantity: int, date_added: datetime):
        pass

    def remove_item(self, item: str, quantity: int):
        for _ in range(quantity):
            self.shopping_list.remove(item)


class TestRepeatingItems(RepeatingItems):

    def __init__(self, repeating_items: list):
        self.repeating_items = repeating_items

    def get_repeating_items(self) -> list:
        return self.repeating_items

    def add_repeating_item(self, item: str):
        pass


@pytest.fixture
def setup_shopping_manager(request):
    if not hasattr(request, 'param'):
        purchases = None
        repeating_items = None
        meal_plan = None
        shopping_list = None
    else:
        purchases, repeating_items, meal_plan, shopping_list = request.param

    if purchases is None:
        purchases = []
    if repeating_items is None:
        repeating_items = []
    if meal_plan is None:
        meal_plan = {TestDays.DAY_1: [], TestDays.DAY_2: []}
    if shopping_list is None:
        shopping_list = []

    meal_plan = TestMealPlan(meal_plan, lambda: CURRENT_TIME, TestDays)
    shopping_history = TestShoppingHistory(purchases)
    shopping_list = TestShoppingList(shopping_list)
    repeating_items = TestRepeatingItems(repeating_items)

    shopping_manager = ShoppingManager(meal_plan,
                                       shopping_history,
                                       shopping_list,
                                       repeating_items,
                                       TestDays,
                                       lambda: CURRENT_TIME + timedelta(days=1))

    return shopping_manager, shopping_list, meal_plan, shopping_history


_setup_shopping_manager = setup_shopping_manager


def test_todays_items_no_items_is_empty_list(_setup_shopping_manager):
    shopping_manager, _, _, _ = _setup_shopping_manager

    items = shopping_manager.todays_items()

    assert items == []


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           None,
                           None)],
                         indirect=True)
def test_todays_items_with_repeating_items(_setup_shopping_manager):
    shopping_manager, _, _, _ = _setup_shopping_manager

    items = shopping_manager.todays_items()

    assert items == [TEST_ITEM]


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           {TestDays.DAY_1: [TEST_ITEM_2], TestDays.DAY_2: [TEST_ITEM_2]},
                           [TEST_ITEM_3])],
                         indirect=True)
def test_todays_items_multiple_items(_setup_shopping_manager):
    shopping_manager, _, _, _ = _setup_shopping_manager

    items = shopping_manager.todays_items()

    assert items == [TEST_ITEM, TEST_ITEM_2, TEST_ITEM_2, TEST_ITEM_3]


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           {TestDays.DAY_1: [TEST_ITEM], TestDays.DAY_2: [TEST_ITEM]},
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_shopping_list_is_most_important(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 1)

    assert shopping_manager.todays_items() == [TEST_ITEM, TEST_ITEM]
    assert TEST_ITEM not in shopping_list.get_items()
    assert not meal_plan.is_meal_purchased(TestDays.DAY_1)
    assert not meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           {TestDays.DAY_1: [TEST_ITEM], TestDays.DAY_2: [TEST_ITEM]},
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_extra_items_are_used(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 2)

    assert shopping_manager.todays_items() == [TEST_ITEM]
    assert TEST_ITEM not in shopping_list.get_items()
    assert not meal_plan.is_meal_purchased(TestDays.DAY_1)
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           {TestDays.DAY_1: [TEST_ITEM], TestDays.DAY_2: [TEST_ITEM]},
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_two_meals_are_purchased(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 3)

    assert shopping_manager.todays_items() == []
    assert TEST_ITEM not in shopping_list.get_items()
    assert meal_plan.is_meal_purchased(TestDays.DAY_1)
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           {TestDays.DAY_1: [TEST_ITEM], TestDays.DAY_2: [TEST_ITEM]},
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_repeating_item(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 4)

    assert shopping_manager.todays_items() == []
    assert TEST_ITEM not in shopping_list.get_items()
    assert meal_plan.is_meal_purchased(TestDays.DAY_1)
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           {TestDays.DAY_1: [TEST_ITEM], TestDays.DAY_2: [TEST_ITEM]},
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_not_repeating_item(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    with pytest.raises(UnexpectedBuyException):
        shopping_manager.complete_item(TEST_ITEM, 4)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           {TestDays.DAY_1: [], TestDays.DAY_2: [TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3]},
                           [])],
                         indirect=True)
def test_complete_item_completing_meal_removes_all_items(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    extra_removed_items = shopping_manager.complete_item(TEST_ITEM, 1)

    assert extra_removed_items == [[TEST_ITEM_2, 1], [TEST_ITEM_3, 2]]
    assert shopping_manager.todays_items() == []
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)
    assert not meal_plan.is_meal_purchased(TestDays.DAY_1)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           {TestDays.DAY_1: [], TestDays.DAY_2: [TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3]},
                           [])],
                         indirect=True)
def test_complete_today(_setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = _setup_shopping_manager

    shopping_manager.complete_today()

    assert shopping_manager.todays_items() == []
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)
    assert not meal_plan.is_meal_purchased(TestDays.DAY_1)


@pytest.mark.parametrize("_setup_shopping_manager",
                         [([],
                           [' '],
                           {TestDays.DAY_1: [], TestDays.DAY_2: [TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3]},
                           [])],
                         indirect=True)
def test_complete_item(_setup_shopping_manager):
    shopping_manager, _, _, shopping_history = _setup_shopping_manager

    shopping_manager.complete_item(' ', 1)

    assert len(shopping_history.get_all_purchases()) == 0
