from configuration import spreadsheet
from helpers.worksheets import init_worksheet
from todo.todo_list_worksheet import TodoListWorksheet

todo_list_worksheet = init_worksheet(spreadsheet, "TODO")

todo_list = TodoListWorksheet(todo_list_worksheet)
