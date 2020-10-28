import gspread

from shopping.repeatingitems.shopping_repeating_items import RepeatingItems


class RepeatingItemsWorksheet(RepeatingItems):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def get_repeating_items(self) -> list:
        return list(map(lambda x: x[0], self.worksheet.get_all_values()))

    def add_repeating_item(self, item: str):
        self.worksheet.insert_row([item], 0)
