import datetime

import gspread

from helpers.datetime import datetime_to_string


class SpreadsheetHelper(object):

    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self.spreadsheet = spreadsheet
        self.list_worksheet = self.spreadsheet.worksheet("List")
        self.todo_worksheet = self.spreadsheet.worksheet("todo")

    def clear_list(self):
        self.list_worksheet.clear()

    def set_list(self, item: str, quantity: int, date_added: datetime.datetime):
        self.clear_list()
        self.list_worksheet.insert_row([item, str(quantity), datetime_to_string(date_added)])

    def set_repeating_items(self, items: list):
        repeating_worksheet = self.spreadsheet.worksheet("RepeatingItems")
        repeating_worksheet.clear()
        for item in items:
            repeating_worksheet.insert_row([item])

    def clear_todo(self):
        self.todo_worksheet.clear()

    def add_todo_item(self, desc: str, status: str):
        self.todo_worksheet.insert_row([desc, status, "07/06/2023, 00:57:32"], index=2)
