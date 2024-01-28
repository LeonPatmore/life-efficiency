import datetime
from math import floor

from todo.weekly.todo_weekly_manager import TodoWeeklyManager, WeeklyTodo


class TodoWeeklyManagerDynamo(TodoWeeklyManager):

    START_TIME = datetime.datetime(year=2024, month=1, day=1)

    def __init__(self, table, time_provider: callable):
        self.time_provider = time_provider
        self.table = table

    def _get_time_id(self) -> int:
        time_difference = self.time_provider() - self.START_TIME
        return floor(time_difference.days / 7.0)

    def get_todos(self) -> list[WeeklyTodo]:
        time_id = self._get_time_id()
        todos = list()
        for item in self.table.scan()["Items"]:
            is_complete = int(getattr(item, f"Week_{time_id}", 0))
            todos.append(WeeklyTodo(number=int(item["id"]),
                                    day=int(item["Day"]),
                                    desc=item["Desc"],
                                    complete=is_complete == 1))
        return todos

    def complete_todo_for_item(self, number: int):
        time_id = self._get_time_id()
        self.table.update_item(Key={"id": str(number)},
                               UpdateExpression=f"set Week_{time_id}=:s",
                               ExpressionAttributeValues={":s": 1})
