import gspread


class SpreadsheetHelper(object):

    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self.spreadsheet = spreadsheet
        self.list_worksheet = self.spreadsheet.worksheet("List")

    def clear_list(self):
        self.list_worksheet.clear()

    def set_list(self, item: str, quantity: int):
        self.clear_list()
        self.list_worksheet.insert_row([item, str(quantity)])

    def set_repeating_items(self, items: list):
        repeating_worksheet = self.spreadsheet.worksheet("RepeatingItems")
        repeating_worksheet.clear()
        for item in items:
            repeating_worksheet.insert_row([item])
