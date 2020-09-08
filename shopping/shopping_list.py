import gspread


class ShoppingList(object):

    def add_item(self, item: str):
        raise NotImplementedError()


class ShoppingListWorksheet(ShoppingList):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def add_item(self, item: str):
        self.worksheet.insert_row([item], 1)

