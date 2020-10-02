import logging

import gspread

from helpers.datetime import datetime_to_string, string_to_datetime
from todo.todo_list import TodoList, Todo


class TodoListWorksheet(TodoList):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def add_todo(self, todo: Todo):
        self.worksheet.insert_row([todo.desc, datetime_to_string(todo.date_added), datetime_to_string(todo.alert_date)])

    def get_todos(self) -> list:
        rows = self.worksheet.get_all_values()
        todos = list()
        for row in rows:
            # noinspection PyBroadException
            try:
                desc = row[0]
                date_added = string_to_datetime(row[1])
                alert_date = string_to_datetime(row[2])
                todos.insert(Todo(desc, alert_date, date_added))
            except Exception:
                logging.warning("Can not parse row [ {} ]".format(row))
        return todos
