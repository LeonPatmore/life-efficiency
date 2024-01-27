import datetime
from math import floor

from gspread import Worksheet

from helpers.datetime import string_to_datetime, datetime_to_string
from todo.weekly.todo_weekly_manager import TodoWeeklyManager, WeeklyTodo

# TODO: This needs to be fixed.
class TodoWeeklyManagerDynamo(TodoWeeklyManager):

    START_TIME = datetime.datetime(year=2024, month=1, day=1)

    def __init__(self, weekly_todo_table, weekly_todo_history_table, time_provider: callable):
        self.time_provider = time_provider
        self.weekly_todo_table = weekly_todo_table
        self.weekly_todo_history_table = weekly_todo_history_table

    def _get_time_id(self) -> int:
        time_difference = self.time_provider() - self.START_TIME
        return floor(time_difference.days / 7.0)

    def get_todos(self) -> list[WeeklyTodo]:
        return [WeeklyTodo(number=x["Id"],
                           day=int(x["Day"]),
                           desc=x["Desc"],
                           complete=int(x["Complete"]) == 1)
                for x in self.weekly_todo_table.scan()["Items"]]

    def complete_todo_for_item(self, number: int):
        self.table.update_item(Key={"Id": f""},
                               UpdateExpression="set Complete=:c",
                               ExpressionAttributeValues={":c": 1})
        day = self._get_row_for_number(number)
        if day:
            self.worksheet.update_cell(day, self._get_current_column_number(), TodoWeeklyManagerWorksheet.DONE_VALUE)
