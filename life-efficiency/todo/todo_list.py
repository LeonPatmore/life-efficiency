from datetime import datetime

from helpers.datetime import get_current_datetime_utc


class Todo(object):

    def __init__(self, desc: str, alert_date: datetime, date_added: datetime = get_current_datetime_utc()):
        self.desc = desc
        self.alert_date = alert_date
        self.date_added = date_added


class TodoList(object):

    def add_todo(self, todo: Todo):
        raise NotImplementedError()

    def get_todos(self) -> list:
        raise NotImplementedError()
