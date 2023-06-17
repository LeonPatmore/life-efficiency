import logging

from gspread import Worksheet

from helpers.datetime import string_to_datetime, datetime_to_string
from todo.todo_manager import TodoManager, TodoItem, TodoStatus


class TodoManagerWorksheet(TodoManager):

    def __init__(self, worksheet: Worksheet, current_time_provider: callable):
        self.worksheet = worksheet
        self.current_time_provider = current_time_provider

    def get_items(self) -> list[TodoItem]:
        return [TodoItem(x[1],
                         getattr(TodoStatus, x[2]),
                         string_to_datetime(x[3]),
                         item_number=int(x[0]),
                         date_done=string_to_datetime(x[4]) if len(x) > 4 and x[4] else None)
                for x in self.worksheet.get_all_values()[1:]]

    def _get_new_item_count(self) -> int:
        col_vals = reversed(list(enumerate(self.worksheet.col_values(1))))
        first_non_empty_row = next(filter(lambda x: x[1] is not None and x[1] != "", col_vals))
        return first_non_empty_row[0] + 1

    def add_item(self, item: TodoItem):
        if item.item_number is not None:
            item_number = item.item_number
        else:
            item_number = self._get_new_item_count()
        self.worksheet.insert_row([item_number,
                                   item.desc,
                                   item.status.name,
                                   datetime_to_string(item.date_added),
                                   datetime_to_string(item.date_done) if item.date_done else ""],
                                  item_number + 1)

    def get_item(self, item_id: int) -> TodoItem:
        logging.info(f"Getting item with ID [ {item_id} ]")
        logging.info(self.worksheet.get_all_values())
        row = self.worksheet.get_all_values()[item_id]
        return TodoItem(row[1],
                        getattr(TodoStatus, row[2]),
                        string_to_datetime(row[3]),
                        item_number=int(row[0]),
                        date_done=string_to_datetime(row[4]) if len(row) > 4 and row[4] else None)

    def update_item(self, item_id: int, status: TodoStatus):
        self.worksheet.update_cell(item_id + 1, 3, status.name)
        if status == TodoStatus.done:
            self.worksheet.update_cell(item_id + 1, 5, datetime_to_string(self.current_time_provider()))
