from datetime import datetime, timedelta

import pytest

from helpers.datetime import get_current_datetime_utc
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.list.shopping_list import ShoppingList, ShoppingListItem
from shopping.mealplan.meal_plan import MealPlan, MealPlanService
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems
from shopping.shopping_manager import ShoppingManager, UnexpectedBuyException

MEAL_PLAN_WEEKS = 2
CURRENT_TIME = datetime(2001, 1, 1, 1, 1, 1, 1)
TEST_ITEM = "test-item"
TEST_ITEM_2 = "test-item-2"
TEST_ITEM_3 = "test-item-3"


class MealPlanTestImplementation(MealPlanService):

    def __init__(self, meal_plan: list[MealPlan], time_provider: callable):
        self._meal_plan = meal_plan
        super().__init__(time_provider)
        self.meal_purchased = len(meal_plan) * [False]

    def _load_meal_plans(self) -> list[MealPlan]:
        return self._meal_plan

    def _set_current_cycle_start_time(self, current_cycle_start_time: datetime):
        pass

    def _get_current_cycle_start_time(self) -> datetime:
        return CURRENT_TIME

    def _is_meal_purchased(self, index: int) -> bool:
        return self.meal_purchased[index]

    def _set_meal_purchased(self, index: int, purchased: bool):
        self.meal_purchased[index] = purchased


class ShoppingHistoryTestImplementation(ShoppingHistory):

    def __init__(self, purchases: list):
        self.purchases = purchases
        super().__init__()

    def _load_all_purchases(self) -> list:
        return self.purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.purchases.append(purchase)


class ShoppingListTestImplementation(ShoppingList):

    def __init__(self):
        super().__init__(get_current_datetime_utc)
        self.shopping_list = {}

    def get_items(self) -> list[ShoppingListItem]:
        return list(self.shopping_list.values())

    def add_item(self, item: ShoppingListItem):
        self.shopping_list[item.name] = item

    def remove_item(self, item_name: str):
        self.shopping_list.pop(item_name)

    def set_item_quantity(self, item_name: str, quantity: int):
        self.shopping_list[item_name].quantity = quantity


class RepeatingItemsTestImplementation(RepeatingItems):

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
        meal_plan = [MealPlan([]), MealPlan([])]
    if shopping_list is None:
        shopping_list = []

    meal_plan_service = MealPlanTestImplementation(meal_plan, lambda: CURRENT_TIME)
    shopping_history = ShoppingHistoryTestImplementation(purchases)
    test_shopping_list = ShoppingListTestImplementation()
    for item in shopping_list:
        test_shopping_list.increase_quantity(item, 1)
    repeating_items = RepeatingItemsTestImplementation(repeating_items)

    shopping_manager = ShoppingManager(meal_plan_service,
                                       shopping_history,
                                       test_shopping_list,
                                       repeating_items,
                                       lambda: CURRENT_TIME + timedelta(days=1))

    return shopping_manager, test_shopping_list, meal_plan_service, shopping_history


def test_today_items_no_items_is_empty_list(setup_shopping_manager):
    shopping_manager, _, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == []


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           None,
                           None)],
                         indirect=True)
def test_today_items_with_repeating_items(setup_shopping_manager):
    shopping_manager, _, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == [TEST_ITEM]


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [MealPlan([TEST_ITEM_2]), MealPlan([TEST_ITEM_2])],
                           [TEST_ITEM_3])],
                         indirect=True)
def test_today_items_multiple_items(setup_shopping_manager):
    shopping_manager, _, _, _ = setup_shopping_manager

    items = shopping_manager.today_items()

    assert items == [TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3]


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [MealPlan([TEST_ITEM_2]), MealPlan([TEST_ITEM])],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_shopping_list_is_most_important(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan_service, _ = setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 1)

    assert shopping_manager.today_items() == [TEST_ITEM_2]
    assert TEST_ITEM not in shopping_list.get_items()
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(0)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [MealPlan([TEST_ITEM]), MealPlan([TEST_ITEM]), MealPlan([TEST_ITEM])],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_extra_items_are_used(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan_service, _ = setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 2)

    assert shopping_manager.today_items() == []
    assert TEST_ITEM not in shopping_list.get_items()
    assert meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(0)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(2)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [TEST_ITEM],
                           [MealPlan([TEST_ITEM]), MealPlan([TEST_ITEM]), MealPlan([TEST_ITEM])],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_repeating_item(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan_service, _ = setup_shopping_manager

    shopping_manager.complete_item(TEST_ITEM, 6)

    assert shopping_manager.today_items() == []
    assert TEST_ITEM not in shopping_list.get_items()
    assert meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(0)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(2)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           [MealPlan([TEST_ITEM_2]), MealPlan([TEST_ITEM]), MealPlan([TEST_ITEM])],
                           [TEST_ITEM])],
                         indirect=True)
def test_complete_item_too_many_purchased_but_is_not_repeating_item(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan, _ = setup_shopping_manager

    with pytest.raises(UnexpectedBuyException):
        shopping_manager.complete_item(TEST_ITEM, 4)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           [MealPlan([TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3]), MealPlan([])],
                           [])],
                         indirect=True)
def test_complete_item_completing_meal_removes_all_items(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan_service, _ = setup_shopping_manager

    extra_removed_items = shopping_manager.complete_item(TEST_ITEM, 1)

    assert extra_removed_items == [[TEST_ITEM_2, 1], [TEST_ITEM_3, 2]]
    assert shopping_manager.today_items() == []
    assert meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(0)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=4)),
                            ShoppingItemPurchase(TEST_ITEM, 1, CURRENT_TIME - timedelta(days=3))],
                           [],
                           [MealPlan([TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3]), MealPlan([])],
                           [])],
                         indirect=True)
def test_complete_today(setup_shopping_manager):
    shopping_manager, shopping_list, meal_plan_service, _ = setup_shopping_manager

    shopping_manager.complete_today()

    assert shopping_manager.today_items() == []
    assert meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(0)
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)


@pytest.mark.parametrize("setup_shopping_manager",
                         [([],
                           [' '],
                           [MealPlan([]), MealPlan([TEST_ITEM]),
                            MealPlan([TEST_ITEM, TEST_ITEM_2, TEST_ITEM_3, TEST_ITEM_3])],
                           [])],
                         indirect=True)
def test_complete_item(setup_shopping_manager):
    shopping_manager, _, _, shopping_history = setup_shopping_manager

    shopping_manager.complete_item(' ', 1)

    assert len(shopping_history.get_all_purchases()) == 0
