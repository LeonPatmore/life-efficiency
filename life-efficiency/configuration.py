import gspread

from shopping.history.shopping_history import ShoppingHistoryWorksheet
from shopping.predictor.shopping_predictor import ShoppingPredictor
from shopping.shopping_items import ShoppingItems

gc = gspread.service_account(filename="credentials.json")
spreadsheet = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/12vPGwr5Ds3ZygiHf0-XXVXuOZFhH7VTLrWioUroeUbA/edit#gid=0")

if not [x for x in spreadsheet.worksheets() if x.title == "History"]:
    spreadsheet.add_worksheet('History', 100, 100)
shopping_history_worksheet = ShoppingHistoryWorksheet(spreadsheet.worksheet("History"))

shopping_predictor = ShoppingPredictor(shopping_history_worksheet)

repeating_items = [
    ShoppingItems.CHOCOLATE_MILKSHAKE,
    ShoppingItems.APPLES,
    ShoppingItems.GRAPES,
    ShoppingItems.PEARS,
    ShoppingItems.MOUTHWASH
]
