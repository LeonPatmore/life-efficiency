from datetime import datetime
from unittest.mock import Mock, call

import pytest

from todo.todo_manager import TodoStatus, TodoItem
from todo.todo_manager_spreadsheet import TodoManagerWorksheet


CANCELLED_ROW = [1, 'some todo task', 'cancelled', '07/06/2023, 00:57:32']
DONE_ROW = [2, 'some todo task', 'done', '07/06/2023, 00:57:32']
DATETIME = datetime(1, 1, 1, 1, 1, 1)


@pytest.fixture
def setup_todo_manager_worksheet_with_values(request):
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param
    return TodoManagerWorksheet(worksheet_mock, lambda: DATETIME), worksheet_mock


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[]]], indirect=True)
def test_get_items_empty_response(setup_todo_manager_worksheet_with_values):
    todo_manager, _ = setup_todo_manager_worksheet_with_values
    items = todo_manager.get_items()

    assert len(items) == 0


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[], CANCELLED_ROW]], indirect=True)
def test_get_items_with_items(setup_todo_manager_worksheet_with_values):
    todo_manager, _ = setup_todo_manager_worksheet_with_values
    items = todo_manager.get_items()

    assert len(items) == 1
    assert items[0].item_number == 1
    assert items[0].desc == "some todo task"
    assert items[0].status == TodoStatus.cancelled
    assert items[0].date_added == datetime(year=2023, month=6, day=7, hour=0, minute=57, second=32)


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[], CANCELLED_ROW, DONE_ROW]], indirect=True)
def test_get_item(setup_todo_manager_worksheet_with_values):
    todo_manager, _ = setup_todo_manager_worksheet_with_values
    item = todo_manager.get_item(2)

    assert item.item_number == 2
    assert item.desc == "some todo task"
    assert item.status == TodoStatus.done
    assert item.date_added == datetime(year=2023, month=6, day=7, hour=0, minute=57, second=32)


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[]]], indirect=True)
def test_add_item(setup_todo_manager_worksheet_with_values):
    todo_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    todo_manager.add_item(TodoItem("some desc", TodoStatus.not_started, DATETIME, 1, DATETIME))

    worksheet_mock.insert_row.assert_called_once_with(
        [1, 'some desc', 'not_started', '01/01/0001, 01:01:01', '01/01/0001, 01:01:01'], 2)


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[]]], indirect=True)
def test_update_item_not_done_does_not_update_date_done(setup_todo_manager_worksheet_with_values):
    todo_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    todo_manager.update_item(1, TodoStatus.not_started)

    assert call(2, 5, '01/01/0001, 01:01:01') not in worksheet_mock.update_cell.mock_calls


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[]]], indirect=True)
def test_update_item_to_done_does_update_date_done(setup_todo_manager_worksheet_with_values):
    todo_manager, worksheet_mock = setup_todo_manager_worksheet_with_values
    todo_manager.update_item(1, TodoStatus.done)

    worksheet_mock.update_cell.assert_any_call(2, 5, '01/01/0001, 01:01:01')
