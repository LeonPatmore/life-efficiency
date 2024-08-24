from dataclasses import dataclass


@dataclass
class WeeklySet:
    id: str
    name: str


class WeeklyTodo:

    def __init__(self, set_id: str, number: int, day: int, desc: str, complete: bool):
        self.set_id = set_id
        self.number = number
        self.day = day
        self.desc = desc
        self.complete = complete

    def to_json(self) -> dict:
        return {
            "id": self.number,
            "set_id": self.set_id,
            "day": self.day,
            "desc": self.desc,
            "complete": self.complete
        }


class TodoWeeklyManager:

    def get_sets(self) -> list[WeeklySet]:
        raise NotImplementedError

    def get_todos(self) -> list[WeeklyTodo]:
        raise NotImplementedError

    def get_todos_by_set_id(self, set_id: str) -> list[WeeklyTodo]:
        raise NotImplementedError

    def get_ordered_todos(self):
        return sorted(self.get_todos(), key=lambda x: x.day)

    def get_todos_with_filters(self, day: int or None = None, set_id: str or None = None) -> list[WeeklyTodo]:
        def todo_filter(todo: WeeklyTodo):
            return (day is None or todo.day == day) and (set_id is None or todo.set_id == set_id)
        return list(filter(todo_filter, self.get_ordered_todos()))

    def complete_todo_for_item(self, number: int):
        raise NotImplementedError
