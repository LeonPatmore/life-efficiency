import gspread

from shopping.shopping_list import ShoppingListWorksheet


def main():
    gc = gspread.service_account(filename="credentials.json")
    spreadsheet = gc.open_by_url(
        "https://docs.google.com/spreadsheets/d/12vPGwr5Ds3ZygiHf0-XXVXuOZFhH7VTLrWioUroeUbA/edit#gid=0")

    shopping_list_worksheet = spreadsheet.worksheet("Sheet1")
    shopping_list = ShoppingListWorksheet(shopping_list_worksheet)
    shopping_list.add_item("hello")


if __name__ == '__main__':
    main()
