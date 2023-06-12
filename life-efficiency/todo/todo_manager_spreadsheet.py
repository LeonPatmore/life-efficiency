from gspread import Worksheet

from todo.todo_manager import TodoManager, TodoItem, TodoStatus


class TodoManagerWorksheet(TodoManager):

    def __init__(self, worksheet: Worksheet):
        self.worksheet = worksheet

    def get_items(self) -> list[TodoItem]:
        return [TodoItem(x[0], TodoStatus(x[1])) for x in self.worksheet.get_all_values()]

    def add_item(self, item: TodoItem):
        pass
