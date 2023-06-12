from datetime import datetime
from enum import Enum

from helpers.datetime import datetime_to_string


class TodoStatus(Enum):
    not_started = 0
    in_progress = 1
    done = 2
    cancelled = 3


class TodoItem:

    def __init__(self, desc: str, status: TodoStatus, date_added: datetime):
        self.desc = desc
        self.status = status
        self.date_added = date_added

    def to_json(self):
        return {
            "desc": self.desc,
            "status": self.status.name,
            "date_added": datetime_to_string(self.date_added)
        }


class TodoManager:

    def get_items(self) -> list[TodoItem]:
        raise NotImplementedError

    def add_item(self, item: TodoItem):
        raise NotImplementedError
