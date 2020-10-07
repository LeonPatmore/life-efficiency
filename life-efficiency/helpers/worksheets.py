from gspread import Spreadsheet, Worksheet


def init_worksheet(spreadsheet: Spreadsheet, title: str) -> Worksheet:
    if not [x for x in spreadsheet.worksheets() if x.title == title]:
        return spreadsheet.add_worksheet(title, 100, 100)
    return spreadsheet.worksheet(title)
