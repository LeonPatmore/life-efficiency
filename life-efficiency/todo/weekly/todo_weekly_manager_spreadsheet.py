from math import floor

from gspread import Worksheet

from helpers.datetime import string_to_datetime, datetime_to_string
from todo.weekly.todo_weekly_manager import TodoWeeklyManager, WeeklyTodo


class TodoWeeklyManagerWorksheet(TodoWeeklyManager):

    DONE_VALUE = "done"

    def __init__(self, worksheet: Worksheet, time_provider: callable):
        self.time_provider = time_provider
        self.worksheet = worksheet
        self._init_worksheet()
        self.start_time = string_to_datetime(self.worksheet.get("A1").first())

    def _init_worksheet(self):
        worksheet_values = self.worksheet.get_all_values()
        if not worksheet_values \
                or len(worksheet_values) == 0 \
                or len(worksheet_values[0]) == 0 \
                or worksheet_values[0][0] == "":
            self.worksheet.update_cell(1, 1, datetime_to_string(self.time_provider()))

    def get_todos(self) -> list[WeeklyTodo]:
        return [WeeklyTodo(int(row[0]), int(row[1]), row[2], self._is_complete(row))
                for row in self.worksheet.get_all_values()[1:]]

    def _is_complete(self, row):
        current_col = self._get_current_column_number()
        index = current_col - 1
        if len(row) > index:
            return row[index] == TodoWeeklyManagerWorksheet.DONE_VALUE
        else:
            return False

    def _get_row_for_number(self, number: int) -> int or None:
        for i, row in enumerate(self.worksheet.get_all_values()[1:]):
            if row[0] == number:
                return i + 2
        return None

    def _get_current_column_number(self) -> int:
        time_difference = self.time_provider() - self.start_time
        return floor(time_difference.days / 7.0) + 4

    def complete_todo_for_item(self, number: int):
        day = self._get_row_for_number(number)
        if day:
            self.worksheet.update_cell(day, self._get_current_column_number(), TodoWeeklyManagerWorksheet.DONE_VALUE)
