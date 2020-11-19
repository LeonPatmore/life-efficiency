import gspread


class SpreadsheetHelper(object):

    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self.spreadsheet = spreadsheet

    def set_list(self, item: str, quantity: int):
        list_worksheet = self.spreadsheet.worksheet("List")
        list_worksheet.clear()
        self.spreadsheet.worksheet("List").insert_row([item, str(quantity)])
