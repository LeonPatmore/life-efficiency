from datetime import datetime
from enum import Enum

from helpers.datetime import datetime_to_string


class TodoStatus(Enum):
    not_started = 0
    in_progress = 1
    done = 2
    cancelled = 3


class TodoItem:

    def __init__(self,
                 desc: str,
                 status: TodoStatus,
                 date_added: datetime,
                 item_number: int = None,
                 date_done: datetime = None):
        self.desc = desc
        self.status = status
        self.date_added = date_added
        self.item_number = item_number
        self.date_done = date_done

    def to_json(self):
        return {
            "id": self.item_number,
            "desc": self.desc,
            "status": self.status.name,
            "date_added": datetime_to_string(self.date_added),
            "date_done": datetime_to_string(self.date_done) if self.date_done else None
        }


class TodoListManager:

    def get_items(self) -> list[TodoItem]:
        raise NotImplementedError

    def get_item(self, item_id: int) -> TodoItem:
        raise NotImplementedError

    def add_item(self, item: TodoItem):
        raise NotImplementedError

    def update_item(self, item_id: int, status: TodoStatus):
        raise NotImplementedError

    def remove_item(self, item_id: int):
        raise NotImplementedError
