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
                 item_id: str = None,
                 date_done: datetime = None):
        self.desc = desc
        self.status = status
        self.date_added = date_added
        self.item_id = item_id
        self.date_done = date_done

    def to_json(self):
        return {
            "id": self.item_id,
            "desc": self.desc,
            "status": self.status.name,
            "date_added": datetime_to_string(self.date_added),
            "date_done": datetime_to_string(self.date_done) if self.date_done else None
        }


class TodoListManager:

    def get_items(self) -> list[TodoItem]:
        raise NotImplementedError

    def get_item(self, item_id: str) -> TodoItem:
        raise NotImplementedError

    def add_item(self, item: TodoItem) -> TodoItem:
        raise NotImplementedError

    def update_item(self, item_id: str, status: TodoStatus):
        raise NotImplementedError

    def remove_item(self, item_id: str):
        raise NotImplementedError
