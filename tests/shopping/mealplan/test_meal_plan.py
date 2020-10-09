import pytest

from helpers.datetime import Day
from shopping.mealplan.meal_plan import MealPlan


@pytest.fixture
def setup_meal_plan_with_meal():
    meal_day = Day.MONDAY
    items = ["item-one", "item-two"]
    meal_plan = MealPlan()
    meal_plan.add_meal(meal_day, items)
    return meal_plan, meal_day, items


_setup_meal_plan_with_meal = setup_meal_plan_with_meal


def test_meal_plan_day_matches(_setup_meal_plan_with_meal):
    meal_plan, meal_day, items = _setup_meal_plan_with_meal

    discovered_items = meal_plan.get_meal_for_day(meal_day)
    assert items == discovered_items


def test_meal_plan_day_not_matching(_setup_meal_plan_with_meal):
    meal_plan, meal_day, items = _setup_meal_plan_with_meal

    discovered_items = meal_plan.get_meal_for_day(Day.THURSDAY)
    assert [] == discovered_items


def test_meal_plan_append_items(_setup_meal_plan_with_meal):
    meal_plan, meal_day, items = _setup_meal_plan_with_meal
    new_items = ['new-item']

    meal_plan.add_meal(meal_day, new_items, append=True)

    discovered_items = meal_plan.get_meal_for_day(meal_day)
    assert items + new_items == discovered_items
