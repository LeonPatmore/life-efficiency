from enum import Enum


class TodoStatus(Enum):
    not_started = 0
    in_progress = 1
    done = 2
    cancelled = 3

if __name__ == '__main__':
    print(dir(TodoStatus))


class TodoItem:

    def __init__(self, desc: str, status: TodoStatus):
        self.desc = desc
        self.status = status


class TodoManager:

    def get_items(self) -> list[TodoItem]:
        raise NotImplementedError

    def add_item(self, item: TodoItem):
        raise NotImplementedError
