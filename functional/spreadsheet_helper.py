import gspread


class SpreadsheetHelper(object):

    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self.spreadsheet = spreadsheet

    def set_list(self, item: str, quantity: int):
        list_worksheet = self.spreadsheet.worksheet("List")
        list_worksheet.clear()
        list_worksheet.insert_row([item, str(quantity)])

    def set_repeating_items(self, items: list):
        repeating_worksheet = self.spreadsheet.worksheet("RepeatingItems")
        repeating_worksheet.clear()
        for item in items:
            repeating_worksheet.insert_row([item])
