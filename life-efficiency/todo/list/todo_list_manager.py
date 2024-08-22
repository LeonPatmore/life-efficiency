import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from dynamo.dynamo_repository import dynamo_item
from helpers.datetime import datetime_to_string
from repository.repository import Repository


class TodoStatus(Enum):
    not_started = 0
    in_progress = 1
    done = 2
    cancelled = 3


@dynamo_item("todo-list", {"TodoStatus": "status"})
@dataclass
class TodoItem:
    desc: str
    status: TodoStatus
    date_added: datetime
    id: str = None
    date_done: datetime = None


class TodoListManager(Repository):

    def __init__(self, current_time_provider: callable):
        super().__init__(TodoItem)
        self.current_time_provider = current_time_provider

    def update_item(self, item_id: str, status: TodoStatus):
        logging.info(f"Updating item {item_id} with status {status.name}")
        self.update(item_id, "status", status)
        if status == TodoStatus.done:
            current_time = datetime_to_string(self.current_time_provider())
            self.update(item_id, "date_done", current_time)
