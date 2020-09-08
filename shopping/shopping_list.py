import gspread

from shopping.shopping_item import ShoppingItems


class ShoppingList(object):

    def add_item(self, item: str, amount: int = 1):
        raise NotImplementedError()


class ShoppingListWorksheet(ShoppingList):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def add_item(self, item: ShoppingItems, amount: int = 1):
        self.worksheet.insert_row([item.name, amount], 1)
