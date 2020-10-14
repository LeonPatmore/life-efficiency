import logging
from datetime import datetime

from helpers.datetime import datetime_to_string
from shopping.list.shopping_list import ShoppingList


class ShoppingListWorksheet(ShoppingList):

    def __init__(self, worksheet):
        self.worksheet = worksheet

    def get_items(self) -> list:
        worksheet_values = self.worksheet.get_all_values()
        items = []
        for worksheet_row in worksheet_values:
            # noinspection PyBroadException
            try:
                item = worksheet_row[0]
                quantity = int(worksheet_row[1])
                items.extend([item for _ in range(quantity)])
            except Exception:
                logging.warning("Could not parse row, [ {} ]".format(worksheet_row))
        return items

    def add_item(self, item: str, quantity: int, date_added: datetime):
        self.worksheet.insert_row([item, str(quantity), datetime_to_string(date_added)], 1)
