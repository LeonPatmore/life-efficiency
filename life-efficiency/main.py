import gspread
import click

from shopping.history.shopping_history import ShoppingHistoryWorksheet
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.shopping_items import ShoppingItems
# from shopping.shopping_list import ShoppingListWorksheet
from shopping.shopping_commands import shopping


@click.group()
def main_group():
    pass


@click.command()
@click.option('--force', '-f', default=False, type=bool)
def create():
    gc = gspread.service_account(filename="credentials.json")
    spreadsheet = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/12vPGwr5Ds3ZygiHf0-XXVXuOZFhH7VTLrWioUroeUbA/edit#gid=0")

    # shopping_list_worksheet = spreadsheet.worksheet("Sheet1")
    # shopping_list = ShoppingListWorksheet(shopping_list_worksheet)

    if not [x for x in spreadsheet.worksheets() if x.title == "History"]:
        spreadsheet.add_worksheet('History', 100, 100)
    shopping_history_worksheet = ShoppingHistoryWorksheet(spreadsheet.worksheet("History"))
    shopping_history_worksheet.add_purchase(ShoppingItemPurchase(ShoppingItems.CHOCOLATE_MILKSHAKE, 2))


main_group.add_command(shopping)


if __name__ == '__main__':
    main_group()
