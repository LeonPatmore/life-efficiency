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


@pytest.fixture
def setup_meal_plan(request):
    current_time = datetime(5, 5, 5, 5, 5, 5)
    meal_plan = TestMealPlan(request.param, lambda: current_time, TestDays, 2, current_time - timedelta(days=1))
    return meal_plan


_setup_meal_plan = setup_meal_plan


@pytest.mark.parametrize("_setup_meal_plan", [[{TestDays.DAY_1: ["", "item-1", "", ""]}]], indirect=True)
def test_get_meal_for_day_removes_empty_items(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meals = meal_plan.get_meal_for_day_and_week(TestDays.DAY_1, 0)

    assert meals == ["item-1"]


@pytest.mark.parametrize("_setup_meal_plan", [[{TestDays.DAY_1: ["", "item-1", "", ""]}]], indirect=True)
def test_get_meal_for_day_and_week_same_day_wrong_week(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meals = meal_plan.get_meal_for_day_and_week(TestDays.DAY_1, 1)

    assert meals == []


@pytest.mark.parametrize("_setup_meal_plan", [[{TestDays.DAY_1: ["", "item-1", "", ""]}]], indirect=True)
def test_check_purchase_time_when_not_exceeded_do_nothing(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meal_plan.is_meal_purchased(TestDays.DAY_1, 1)
