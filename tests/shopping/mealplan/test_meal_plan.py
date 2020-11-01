from datetime import datetime
from enum import Enum

import pytest

from shopping.mealplan.meal_plan import MealPlan
from tests.shopping.mealplan.test_days import TestDays


class TestMealPlan(MealPlan):

    def __init__(self, meal_plan: dict, time_provider, days: Enum):
        self._mean_plan = meal_plan
        super().__init__(time_provider, days)

    def _load_meal_plans(self):
        self.mean_plan = self._mean_plan

    def _get_purchase_time(self) -> datetime:
        pass

    def _reset_purchase_time(self, new_time: datetime):
        pass

    def _is_meal_purchased_implementation(self, day) -> bool:
        pass

    def _purchase_meal_implementation(self, day):
        pass


@pytest.fixture
def setup_meal_plan(request):
    meal_plan = TestMealPlan(request.param, lambda: "", TestDays)
    return meal_plan


_setup_meal_plan = setup_meal_plan


@pytest.mark.parametrize("_setup_meal_plan", [{TestDays.DAY_1: ["", "item-1", "", ""]}], indirect=True)
def test_get_meal_for_day_removes_empty_items(_setup_meal_plan):
    meal_plan = _setup_meal_plan

    meals = meal_plan.get_meal_for_day(TestDays.DAY_1)

    assert meals == ["item-1"]
