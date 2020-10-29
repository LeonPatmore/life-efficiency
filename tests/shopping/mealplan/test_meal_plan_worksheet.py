from datetime import datetime, timedelta
from enum import Enum
from unittest.mock import Mock

import pytest

from helpers.datetime import datetime_to_string

CURRENT_DATETIME = datetime(2001, 1, 1, 1, 1, 1, 0)
CURRENT_DATETIME_STRING = datetime_to_string(CURRENT_DATETIME)


class TestDays(Enum):

    DAY_1 = 0
    DAY_2 = 1


@pytest.fixture
def setup_meal_plan_worksheet(request):
    if not hasattr(request, 'param'):
        setattr(request, 'param', ([["some-item-1", "some-item-2"], []],
                                   [[CURRENT_DATETIME_STRING], ["False"], ["False"]]))
    meal_plan_worksheet = Mock()
    meal_plan_worksheet.get_all_values.return_value = request.param[0]

    meal_purchase_worksheet = Mock()
    meal_purchase_worksheet.get_all_values.return_value = request.param[1]

    from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
    meal_plan = MealPlanWorksheet(lambda: CURRENT_DATETIME,
                                  TestDays,
                                  meal_plan_worksheet,
                                  meal_purchase_worksheet)

    return meal_plan, meal_purchase_worksheet


_setup_meal_plan_worksheet = setup_meal_plan_worksheet


def test_get_meal_for_day_with_items(_setup_meal_plan_worksheet):
    meal_plan, _ = _setup_meal_plan_worksheet
    meal = meal_plan.get_meal_for_day(TestDays.DAY_1)
    assert meal == ["some-item-1", "some-item-2"]


def test_get_meal_for_day_with_no_items(_setup_meal_plan_worksheet):
    meal_plan, _ = _setup_meal_plan_worksheet
    meal = meal_plan.get_meal_for_day(TestDays.DAY_2)
    assert meal == []


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], []],
                           [[CURRENT_DATETIME_STRING], [], ['True']])],
                         indirect=True)
def test_is_meal_purchased_is_true(_setup_meal_plan_worksheet):
    meal_plan, _ = _setup_meal_plan_worksheet
    assert meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], []],
                           [[CURRENT_DATETIME_STRING], [], ['False']])],
                         indirect=True)
def test_is_meal_purchased_is_false(_setup_meal_plan_worksheet):
    meal_plan, _ = _setup_meal_plan_worksheet
    assert not meal_plan.is_meal_purchased(TestDays.DAY_2)


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"]],
                           [[CURRENT_DATETIME_STRING], []])],
                         indirect=True)
def test_when_not_enough_meals(_setup_meal_plan_worksheet):
    meal_plan, _ = _setup_meal_plan_worksheet
    assert meal_plan.get_meal_for_day(TestDays.DAY_1) == ["some-item-1", "some-item-2"]
    assert meal_plan.get_meal_for_day(TestDays.DAY_2) == []


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"]],
                           [])],
                         indirect=True)
def test_init_with_empty_meal_purchase_worksheet(_setup_meal_plan_worksheet):
    meal_plan, meal_purchase_worksheet = _setup_meal_plan_worksheet
    meal_purchase_worksheet.update_cell.assert_called_with(3, 1, "False")


def test_purchase_meal(_setup_meal_plan_worksheet):
    meal_plan, meal_purchase_worksheet = _setup_meal_plan_worksheet

    meal_plan.purchase_meal(TestDays.DAY_1)

    meal_purchase_worksheet.update_cell.assert_called_once_with(2, 1, "True")


def test_check_purchase_time_when_same_day(_setup_meal_plan_worksheet):
    meal_plan, meal_purchase_worksheet = _setup_meal_plan_worksheet

    meal_plan.is_meal_purchased(TestDays.DAY_2)

    meal_purchase_worksheet.update_cell.assert_not_called()


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], []],
                           [[datetime_to_string(CURRENT_DATETIME + timedelta(4, 0, 0, 0, 0, 0, 0))], [], ['False']])],
                         indirect=True)
def test_check_purchase_time_when_same_week(_setup_meal_plan_worksheet):
    meal_plan, meal_purchase_worksheet = _setup_meal_plan_worksheet

    meal_plan.is_meal_purchased(TestDays.DAY_2)

    meal_purchase_worksheet.update_cell.assert_not_called()


@pytest.mark.parametrize("_setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], []],
                           [[datetime_to_string(CURRENT_DATETIME + timedelta(7, 0, 0, 0, 0, 0, 0))], [], ['False']])],
                         indirect=True)
def test_check_purchase_time_when_different_week(_setup_meal_plan_worksheet):
    meal_plan, meal_purchase_worksheet = _setup_meal_plan_worksheet

    meal_plan.is_meal_purchased(TestDays.DAY_2)

    meal_purchase_worksheet.update_cell.assert_called()
