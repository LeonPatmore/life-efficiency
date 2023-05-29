import logging

import gspread

from helpers.datetime import datetime_to_string, string_to_datetime
from shopping.list.shopping_list import ShoppingList, ShoppingListItem


class NotEnoughItemsInList(Exception):

    def __init__(self):
        pass


class ShoppingListWorksheet(ShoppingList):

    def __init__(self, worksheet: gspread.Worksheet, current_datetime_generator: callable):
        super().__init__(current_datetime_generator)
        self.worksheet = worksheet

    def get_items(self) -> list[ShoppingListItem]:
        worksheet_values = self.worksheet.get_all_values()
        items = []
        for worksheet_row in worksheet_values:
            # noinspection PyBroadException
            try:
                name = worksheet_row[0]
                quantity = int(worksheet_row[1])
                date_time = string_to_datetime(worksheet_row[2])
                items.append(ShoppingListItem(name, quantity, date_time))
            except Exception as e:
                logging.warning(f"Could not parse row, [ {worksheet_row} ], {e}")

        return items

    def add_item(self, item: ShoppingListItem):
        self.worksheet.insert_row([item.name, str(item.quantity), datetime_to_string(item.date_added)], 1)

    def _for_each_row_matching(self, item_name: str, do: callable):
        worksheet_values = self.worksheet.get_all_values()
        for index, worksheet_row in reversed(list(enumerate(worksheet_values))):
            try:
                if item_name.lower() == worksheet_row[0].lower():
                    do(index, worksheet_row)
            except Exception:
                pass

    def remove_item(self, item_name: str):
        logging.info(f"Removing [ {item_name} ] from shopping list!")
        self._for_each_row_matching(item_name, lambda i, _: self.worksheet.delete_rows(i + 1))

    def set_item_quantity(self, item_name: str, quantity: int):
        current_quantity = self.get_items_map()[item_name].quantity
        if quantity > current_quantity:
            amount_to_add = quantity - current_quantity

            def add_to_first_row(index, worksheet_row):
                nonlocal amount_to_add
                if amount_to_add == 0:
                    return
                this_quantity = int(worksheet_row[1])
                self.worksheet.update_cell(index + 1, 2, str(this_quantity + amount_to_add))
                amount_to_add = 0
            self._for_each_row_matching(item_name, add_to_first_row)
        else:
            amount_to_remove = current_quantity - quantity

            def remove_from_rows_while_we_can(index, worksheet_row):
                nonlocal amount_to_remove
                if amount_to_remove == 0:
                    return
                this_quantity = int(worksheet_row[1])
                amount_to_remove_from_this_row = min(amount_to_remove, this_quantity)
                if amount_to_remove_from_this_row == this_quantity:
                    self.worksheet.delete_rows(index + 1)
                else:
                    self.worksheet.update_cell(index + 1, 2, str(this_quantity - amount_to_remove_from_this_row))
                amount_to_remove -= amount_to_remove_from_this_row
            self._for_each_row_matching(item_name, remove_from_rows_while_we_can)
