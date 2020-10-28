from gspread import Spreadsheet

from helpers.worksheets import init_worksheet
from shopping.history.shopping_history_worksheet import ShoppingHistoryWorksheet
from shopping.list.shopping_list_worksheet import ShoppingListWorksheet
from shopping.shopping_manager import ShoppingManager


class ShoppingManagerSpreadsheet(ShoppingManager):

    def __init__(self, spreadsheet: Spreadsheet, meal_plan, repeating_items):
        shopping_history_worksheet = ShoppingHistoryWorksheet(init_worksheet(spreadsheet, "History"))
        shopping_list_worksheet = ShoppingListWorksheet(init_worksheet(spreadsheet, "List"))
        super(ShoppingManagerSpreadsheet, self).__init__(meal_plan,
                                                         shopping_history_worksheet,
                                                         shopping_list_worksheet,
                                                         repeating_items)
