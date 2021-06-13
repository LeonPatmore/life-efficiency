from datetime import datetime, timedelta
from enum import Enum

import pytest

from shopping.mealplan.meal_plan import MealPlan
from tests.shopping.mealplan.test_days import TestDays


class TestMealPlan(MealPlan):

    def __init__(self, meal_plan: dict, time_provider, days: Enum, weeks: int, purchase_time: datetime):
        self._mean_plan = meal_plan
        self.purchase_time = purchase_time
        self.purchase_time_reset = False
        super().__init__(time_provider, days, weeks)

    def _load_meal_plans(self):
        self.mean_plan = self._mean_plan

    def _get_purchase_time(self) -> datetime:
        return self.purchase_time

    def _reset_purchase_time(self, new_time: datetime):
        self.purchase_time = new_time

    def _is_meal_purchased_implementation(self, day, week) -> bool:
        pass

    def _purchase_meal_implementation(self, day, week):
        pass

    def get_current_week(self) -> int:
        pass

    def get_purchase_time(self):
        return self._get_purchase_time()


CURRENT_TIME = datetime(5, 5, 5, 5, 5, 5)
PURCHASE_TIME = CURRENT_TIME - timedelta(days=1)


@pytest.fixture
def setup_meal_plan(request):
    params = request.param if "param" in dir(request) else {"meal_plan": {}, "current_time": CURRENT_TIME}
    current_time = params["current_time"] if "current_time" in params.keys() else CURRENT_TIME
    meal_plan_dict = params["meal_plan"] if "meal_plan" in params.keys() else {}
    meal_plan = TestMealPlan(meal_plan_dict, lambda: current_time, TestDays, 2, PURCHASE_TIME)
    return meal_plan


_setup_meal_plan = setup_meal_plan


@pytest.mark.parametrize("_setup_meal_plan", [{"meal_plan": {0: {TestDays.DAY_1: ["item-1"]}}}], indirect=True)
def test_get_meal_for_day_removes_empty_items(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meals = meal_plan.get_meal_for_day_and_week(TestDays.DAY_1, 0)

    assert meals == ["item-1"]


@pytest.mark.parametrize("_setup_meal_plan", [{"meal_plan": {0: {TestDays.DAY_1: ["item-1"]}}}], indirect=True)
def test_get_meal_for_day_and_week_same_day_wrong_week(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meals = meal_plan.get_meal_for_day_and_week(TestDays.DAY_1, 1)

    assert meals == []


def test_purchase_meal_when_wrong_week(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    with pytest.raises(ValueError):
        meal_plan.purchase_meal(TestDays.DAY_1, 3)


def test_is_meal_purchased_when_wrong_week(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    with pytest.raises(ValueError):
        meal_plan.is_meal_purchased(TestDays.DAY_1, 3)


@pytest.mark.parametrize("_setup_meal_plan", [{"meal_plan": {0: {TestDays.DAY_1: ["item-1"]}}}], indirect=True)
def test_check_purchase_time_when_not_exceeded_do_nothing(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meal_plan.is_meal_purchased(TestDays.DAY_1, 1)

    assert PURCHASE_TIME == meal_plan.get_purchase_time()


@pytest.mark.parametrize("_setup_meal_plan", [{"meal_plan": {0: {TestDays.DAY_1: ["item-1"]}},
                                               "current_time": PURCHASE_TIME + timedelta(weeks=3)}], indirect=True)
def test_check_purchase_time_when_exceeded_reset_purchase_time(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meal_plan.is_meal_purchased(TestDays.DAY_1, 1)

    assert PURCHASE_TIME + timedelta(weeks=3) == meal_plan.get_purchase_time()
