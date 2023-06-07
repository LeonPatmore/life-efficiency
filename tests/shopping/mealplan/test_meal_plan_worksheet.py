from datetime import datetime, timedelta
from unittest.mock import Mock, call

import pytest

from helpers.datetime import datetime_to_string

CURRENT_DATETIME = datetime(2001, 1, 1, 1, 1, 1, 0)
CURRENT_DATETIME_STRING = datetime_to_string(CURRENT_DATETIME)


@pytest.fixture
def setup_meal_plan_worksheet(request):
    if not hasattr(request, 'param'):
        setattr(request, 'param', ([["some-item-1", "some-item-2"], [], [""], ["some-item-3"]],
                                   [[CURRENT_DATETIME_STRING], ["False"], ["False"], ["True"], ["False"]]))
    meal_plan_worksheet = Mock()
    meal_plan_worksheet.get_all_values.return_value = request.param[0]

    meal_purchase_worksheet = Mock()
    meal_purchase_worksheet.get_all_values.return_value = request.param[1]
    get_mock = Mock()
    if request.param[1]:
        get_mock.first.return_value = request.param[1][0][0]
    else:
        get_mock.first.side_effect = KeyError()
    meal_purchase_worksheet.get.return_value = get_mock

    from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
    meal_plan_service = MealPlanWorksheet(lambda: CURRENT_DATETIME,
                                          meal_plan_worksheet,
                                          meal_purchase_worksheet)

    return meal_plan_service, meal_purchase_worksheet


def test_get_meal_plan_of_current_day_plus_offset(setup_meal_plan_worksheet):
    meal_plan_service, _ = setup_meal_plan_worksheet
    meal_plan = meal_plan_service.get_meal_plan_of_current_day_plus_offset()
    assert meal_plan.items == ["some-item-1", "some-item-2"]


def test_get_meal_plan_of_current_day_plus_offset_with_offset_with_no_items(setup_meal_plan_worksheet):
    meal_plan_service, _ = setup_meal_plan_worksheet
    meal_plan = meal_plan_service.get_meal_plan_of_current_day_plus_offset(1)
    assert meal_plan.items == []


def test_get_meal_plan_of_current_day_plus_offset_with_offset(setup_meal_plan_worksheet):
    meal_plan_service, _ = setup_meal_plan_worksheet
    meal_plan = meal_plan_service.get_meal_plan_of_current_day_plus_offset(2)
    assert meal_plan.items == ["some-item-3"]


@pytest.mark.parametrize("setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], ["some-item-3"]],
                           [[CURRENT_DATETIME_STRING], [], ['True']])],
                         indirect=True)
def test_is_meal_plan_of_current_day_plus_offset_purchased_with_offset(setup_meal_plan_worksheet):
    meal_plan_service, _ = setup_meal_plan_worksheet
    assert meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)


@pytest.mark.parametrize("setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], ["some-item-3"]],
                           [[CURRENT_DATETIME_STRING], [], ['False']])],
                         indirect=True)
def test_is_meal_purchased_is_false(setup_meal_plan_worksheet):
    meal_plan_service, _ = setup_meal_plan_worksheet
    assert not meal_plan_service.is_meal_plan_of_current_day_plus_offset_purchased(1)


@pytest.mark.parametrize("setup_meal_plan_worksheet",
                         [([["some-item-1", "some-item-2"], ["some-item-3"]], [])],
                         indirect=True)
def test_init_with_empty_meal_purchase_worksheet(setup_meal_plan_worksheet):
    _, meal_purchase_worksheet = setup_meal_plan_worksheet
    calls = list()
    calls.append(call(1, 1, '01/01/2001, 01:01:01'))
    for x in range(2, 3):
        calls.append(call(x, 1, "False"))
    meal_purchase_worksheet.update_cell.assert_has_calls(calls)


def test_purchase_meal_plan_of_current_day_plus_offset(setup_meal_plan_worksheet):
    meal_plan_service, meal_purchase_worksheet = setup_meal_plan_worksheet

    meal_plan_service.purchase_meal_plan_of_current_day_plus_offset()

    meal_purchase_worksheet.update_cell.assert_called_once_with(2, 1, "True")


def test_purchase_meal_plan_of_current_day_plus_offset_with_offset(setup_meal_plan_worksheet):
    meal_plan_service, meal_purchase_worksheet = setup_meal_plan_worksheet

    meal_plan_service.purchase_meal_plan_of_current_day_plus_offset(1)

    meal_purchase_worksheet.update_cell.assert_called_once_with(3, 1, "True")
