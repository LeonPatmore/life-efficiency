from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from helpers.datetime import datetime_to_string
from tests.google_spreadsheet_test_helpers import generate_worksheet_mock
from todo.weekly.todo_weekly_manager_spreadsheet import TodoWeeklyManagerWorksheet

CURRENT_TIME_MOCK = Mock()
START_DATE = datetime(1, 1, 1, 1, 1, 1)
START_DATE_STRING = datetime_to_string(START_DATE)
DATE_ROW = [START_DATE_STRING]
COMPLETE_ROW = [1, 2, 'some todo task', "done", "", "done"]
NOT_COMPLETE_ROW = [2, 3, 'some todo task', "", "", ""]
FRIDAY_ROW_1 = [3, 5, 'some todo task', "", "", "done"]
FRIDAY_ROW_2 = [4, 5, 'some todo task', "", "", "done"]


@pytest.fixture
def setup_todo_manager_worksheet_with_values(request) -> tuple:
    worksheet = generate_worksheet_mock(all_values=request.param, get_first=START_DATE_STRING)
    CURRENT_TIME_MOCK.return_value = START_DATE
    return TodoWeeklyManagerWorksheet(worksheet, CURRENT_TIME_MOCK), worksheet


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[DATE_ROW, COMPLETE_ROW]], indirect=True)
def test_get_todo_for_day_single(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, _ = setup_todo_manager_worksheet_with_values
    todos = todo_weekly_manager.get_todo_for_day(2)
    assert len(todos) == 1
    assert todos[0].desc == "some todo task"
    assert todos[0].number == 1
    assert todos[0].complete


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[DATE_ROW, NOT_COMPLETE_ROW]], indirect=True)
def test_get_todo_for_day_single_not_complete(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, _ = setup_todo_manager_worksheet_with_values
    todos = todo_weekly_manager.get_todo_for_day(3)
    assert len(todos) == 1
    assert todos[0].desc == "some todo task"
    assert todos[0].number == 2
    assert not todos[0].complete


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values',
                         [[DATE_ROW, COMPLETE_ROW, FRIDAY_ROW_1, FRIDAY_ROW_2]], indirect=True)
def test_get_todo_for_day_multiple_todos(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, _ = setup_todo_manager_worksheet_with_values
    todos = todo_weekly_manager.get_todo_for_day(5)
    assert len(todos) == 2


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values',
                         [[DATE_ROW, COMPLETE_ROW, FRIDAY_ROW_1, FRIDAY_ROW_2]], indirect=True)
def test_complete_todo_for_day(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    CURRENT_TIME_MOCK.return_value = START_DATE + timedelta(days=1)
    todo_weekly_manager.complete_todo_for_item(1)
    worksheet_mock.update_cell.assert_called_once_with(2, 4, "done")


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values',
                         [[DATE_ROW, COMPLETE_ROW, FRIDAY_ROW_1, FRIDAY_ROW_2]], indirect=True)
def test_complete_todo_for_day_two_weeks(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    CURRENT_TIME_MOCK.return_value = START_DATE + timedelta(weeks=2, days=1)
    todo_weekly_manager.complete_todo_for_item(1)
    worksheet_mock.update_cell.assert_called_once_with(2, 6, "done")


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values',
                         [[DATE_ROW, COMPLETE_ROW, FRIDAY_ROW_1, FRIDAY_ROW_2]], indirect=True)
def test_complete_todo_for_day_when_unknown_number_then_no_update(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    todo_weekly_manager.complete_todo_for_item(10)
    worksheet_mock.update_cell.assert_not_called()


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[]], indirect=True)
def test_init_updates_start_time_if_missing(setup_todo_manager_worksheet_with_values):
    todo_weekly_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    worksheet_mock.update_cell.assert_called_once_with(1, 1, '01/01/0001, 01:01:01')
