from dataclasses import dataclass


@dataclass
class WeeklySet:
    id: str
    name: str


@dataclass
class WeeklyTodo:
    set_id: str
    number: int
    day: int
    desc: str
    complete: bool
    week_frequency: int
    weeks_ago_completed: int

    def to_json(self) -> dict:
        return {
            "id": self.number,
            "set_id": self.set_id,
            "day": self.day,
            "desc": self.desc,
            "complete": self.complete,
            "week_frequency": self.week_frequency
        }


class TodoWeeklyManager:

    def __init__(self, time_provider: callable):
        self.time_provider = time_provider

    def get_sets(self) -> list[WeeklySet]:
        raise NotImplementedError

    def get_todos_for_this_week(self) -> list[WeeklyTodo]:
        return list(filter(lambda x: self.todo_for_this_week(x), self._get_todos()))

    @staticmethod
    def todo_for_this_week(todo: WeeklyTodo) -> bool:
        return not todo.weeks_ago_completed or todo.week_frequency <= todo.weeks_ago_completed

    def _get_todos(self) -> list[WeeklyTodo]:
        raise NotImplementedError

    def get_todos_by_set_id(self, set_id: str) -> list[WeeklyTodo]:
        raise NotImplementedError

    def get_ordered_todos(self):
        return sorted(self.get_todos_for_this_week(), key=lambda x: x.day)

    def get_todos_with_filters(self, day: int or None = None, set_id: str or None = None) -> list[WeeklyTodo]:
        def todo_filter(todo: WeeklyTodo):
            return (day is None or todo.day == day) and (set_id is None or todo.set_id == set_id)
        return list(filter(todo_filter, self.get_ordered_todos()))

    def complete_todo_for_item(self, number: int):
        raise NotImplementedError
