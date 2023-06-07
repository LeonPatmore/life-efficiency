from datetime import datetime, timedelta
from enum import Enum

import pytest

from shopping.mealplan.meal_plan import MealPlanService, MealPlan


class TestMealPlan(MealPlanService):

    def __init__(self, meal_plan: list[MealPlan],
                 time_provider: callable,
                 current_cycle_start_time: datetime):
        self._mean_plan = meal_plan
        self.current_cycle_start_time = current_cycle_start_time
        self.meal_purchased = len(meal_plan) * [False]
        super().__init__(time_provider)

    def _load_meal_plans(self) -> list[MealPlan]:
        return self._mean_plan

    def _set_current_cycle_start_time(self, current_cycle_start_time: datetime):
        self.current_cycle_start_time = current_cycle_start_time

    def _get_current_cycle_start_time(self) -> datetime:
        return self.current_cycle_start_time

    def _is_meal_purchased(self, index: int) -> bool:
        return self.meal_purchased[index]

    def _set_meal_purchased(self, index: int, purchased: bool):
        self.meal_purchased[index] = purchased


CURRENT_TIME = datetime(5, 5, 5, 5, 5, 5)
PURCHASE_TIME = CURRENT_TIME - timedelta(days=1)
ITEM_1 = "item-1"
ITEM_2 = "item-2"


@pytest.fixture
def setup_meal_plan(request) -> TestMealPlan:
    params = request.param if "param" in dir(request) else {"meal_plan": list(), "current_time": CURRENT_TIME}
    cycle_start_time = params["cycle_start_time"] if "cycle_start_time" in params.keys() else CURRENT_TIME
    meal_plan = params["meal_plan"] if "meal_plan" in params.keys() else list()
    meal_plan_service = TestMealPlan(meal_plan, lambda: CURRENT_TIME, cycle_start_time)
    return meal_plan_service


@pytest.mark.parametrize("setup_meal_plan", [{"meal_plan": [MealPlan([ITEM_1])]}], indirect=True)
def test_get_meal_plan_of_current_day_plus_offset(setup_meal_plan):
    meal_plan = setup_meal_plan.get_meal_plan_of_current_day_plus_offset(0)

    assert meal_plan.items == [ITEM_1]


@pytest.mark.parametrize("setup_meal_plan", [{"meal_plan": [MealPlan([]), MealPlan([ITEM_2])]}], indirect=True)
def test_get_meal_plan_of_current_day_plus_offset_with_offset(setup_meal_plan):
    meal_plan = setup_meal_plan.get_meal_plan_of_current_day_plus_offset(1)

    assert meal_plan.items == [ITEM_2]


@pytest.mark.parametrize("setup_meal_plan", [{"meal_plan": [MealPlan([ITEM_1]), MealPlan([ITEM_2])]}], indirect=True)
def test_get_meal_plan_of_current_day_plus_offset_with_offset_greater_than_length_throws_error(setup_meal_plan):
    with pytest.raises(ValueError):
        setup_meal_plan.get_meal_plan_of_current_day_plus_offset(3)


@pytest.mark.parametrize("setup_meal_plan", [{"meal_plan": [MealPlan([ITEM_1]), MealPlan([ITEM_2])],
                                              "cycle_start_time": CURRENT_TIME - timedelta(days=3)}], indirect=True)
def test_get_meal_plan_of_current_day_plus_offset_when_older_than_length(setup_meal_plan):
    meal_plan = setup_meal_plan.get_meal_plan_of_current_day_plus_offset(1)

    assert meal_plan.items == [ITEM_2]
    assert CURRENT_TIME == setup_meal_plan.current_cycle_start_time
