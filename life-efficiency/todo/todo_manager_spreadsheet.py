from gspread import Worksheet

from helpers.datetime import string_to_datetime, datetime_to_string
from todo.todo_manager import TodoManager, TodoItem, TodoStatus


class TodoManagerWorksheet(TodoManager):

    def __init__(self, worksheet: Worksheet):
        self.worksheet = worksheet

    def get_items(self) -> list[TodoItem]:
        return [TodoItem(x[0], getattr(TodoStatus, x[1]), string_to_datetime(x[2]))
                for x in self.worksheet.get_all_values()[1:]]

    def add_item(self, item: TodoItem):
        self.worksheet.insert_row([item.desc, item.status.name, datetime_to_string(item.date_added)], 2)
