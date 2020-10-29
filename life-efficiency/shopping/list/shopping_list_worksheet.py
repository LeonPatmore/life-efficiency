import logging
from datetime import datetime

import gspread

from helpers.datetime import datetime_to_string
from shopping.list.shopping_list import ShoppingList


class NotEnoughItemsInList(Exception):

    def __init__(self):
        pass


class ShoppingListWorksheet(ShoppingList):

    def __init__(self, worksheet: gspread.Worksheet):
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

    def remove_item(self, item: str, quantity: int):
        worksheet_values = self.worksheet.get_all_values()
        for index, worksheet_row in reversed(list(enumerate(worksheet_values))):
            if quantity == 0:
                return
            try:
                this_item = worksheet_row[0]
                if item.lower() == this_item.lower():
                    this_quantity = int(worksheet_row[1])
                    if this_quantity > quantity:
                        new_quantity = this_quantity - quantity
                        self.worksheet.update_cell(index + 1, 2, str(new_quantity))
                        return
                    else:
                        self.worksheet.delete_row(index + 1)
                        quantity = quantity - this_quantity
            except Exception:
                pass

        raise NotEnoughItemsInList()
