from datetime import datetime
from unittest.mock import Mock

import pytest

from todo.todo_manager import TodoStatus
from todo.todo_manager_spreadsheet import TodoManagerWorksheet


CANCELLED_ROW = [1, 'some todo task', 'cancelled', '07/06/2023, 00:57:32']
DONE_ROW = [2, 'some todo task', 'done', '07/06/2023, 00:57:32']


@pytest.fixture
def setup_todo_manager_worksheet_with_values(request):
    worksheet_mock = Mock()
    worksheet_mock.get_all_values.return_value = request.param
    return TodoManagerWorksheet(worksheet_mock)


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[]]], indirect=True)
def test_get_items_empty_response(setup_todo_manager_worksheet_with_values):
    items = setup_todo_manager_worksheet_with_values.get_items()

    assert len(items) == 0


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[], CANCELLED_ROW]], indirect=True)
def test_get_items_with_items(setup_todo_manager_worksheet_with_values):
    items = setup_todo_manager_worksheet_with_values.get_items()

    assert len(items) == 1
    assert items[0].item_number == 1
    assert items[0].desc == "some todo task"
    assert items[0].status == TodoStatus.cancelled
    assert items[0].date_added == datetime(year=2023, month=6, day=7, hour=0, minute=57, second=32)


@pytest.mark.parametrize('setup_todo_manager_worksheet_with_values', [[[], CANCELLED_ROW, DONE_ROW]], indirect=True)
def test_get_item(setup_todo_manager_worksheet_with_values):
    item = setup_todo_manager_worksheet_with_values.get_item(2)

    assert item.item_number == 2
    assert item.desc == "some todo task"
    assert item.status == TodoStatus.done
    assert item.date_added == datetime(year=2023, month=6, day=7, hour=0, minute=57, second=32)
