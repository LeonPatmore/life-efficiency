class WeeklyTodo:

    def __init__(self, number: int, day: int, desc: str, complete: bool):
        self.number = number
        self.day = day
        self.desc = desc
        self.complete = complete

    def to_json(self) -> dict:
        return {
            "id": self.number,
            "day": self.day,
            "desc": self.desc,
            "complete": self.complete
        }


class TodoWeeklyManager:

    def get_todos(self) -> list[WeeklyTodo]:
        raise NotImplementedError

    def get_todo_for_day(self, day: int) -> list[WeeklyTodo]:
        return list(filter(lambda x: x.day == day, self.get_todos()))

    def complete_todo_for_item(self, number: int):
        raise NotImplementedError
