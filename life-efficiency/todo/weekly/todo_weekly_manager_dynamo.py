import datetime
from math import floor

from todo.weekly.todo_weekly_manager import TodoWeeklyManager, WeeklyTodo, WeeklySet


class TodoWeeklyManagerDynamo(TodoWeeklyManager):

    START_TIME = datetime.datetime(year=2024, month=1, day=1)

    def __init__(self, table, weekly_set_table, time_provider: callable):
        self.time_provider = time_provider
        self.table = table
        self.weekly_set_table = weekly_set_table

    def _get_time_id(self) -> int:
        time_difference = self.time_provider() - self.START_TIME
        return floor(time_difference.days / 7.0)

    def get_sets(self) -> list[WeeklySet]:
        return [self._to_weekly_set(x) for x in self.weekly_set_table.scan()["Items"]]

    @staticmethod
    def _to_weekly_set(dynamo_item: dict) -> WeeklySet:
        return WeeklySet(id=dynamo_item["id"], name=dynamo_item["name"])

    def get_todos(self) -> list[WeeklyTodo]:
        time_id = self._get_time_id()
        todos = list()
        for item in self.table.scan()["Items"]:
            is_complete = int(item.get(f"Week_{time_id}", 0))
            todos.append(WeeklyTodo(number=int(item["id"]),
                                    set_id=item["SetId"],
                                    day=int(item["Day"]),
                                    desc=item["Desc"],
                                    complete=is_complete == 1))
        return todos

    def complete_todo_for_item(self, number: int):
        time_id = self._get_time_id()
        self.table.update_item(Key={"id": str(number)},
                               UpdateExpression=f"set Week_{time_id}=:s",
                               ExpressionAttributeValues={":s": 1})
