import logging

import gspread

from helpers.datetime import string_to_datetime, datetime_to_string
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistoryWorksheet(ShoppingHistory):

    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet
        super().__init__()

    def _load_all_purchases(self) -> list:
        worksheet_values = self.worksheet.get_all_values()
        purchases = []
        for worksheet_row in worksheet_values:
            # noinspection PyBroadException
            try:
                item = worksheet_row[0]
                quantity = int(worksheet_row[1])
                datetime = string_to_datetime(worksheet_row[2])
                purchases.append(ShoppingItemPurchase(item, quantity, datetime))
            except Exception:
                logging.warning("Could not parse row, [ {} ]".format(worksheet_row))
        return purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.worksheet.insert_row([purchase.item,
                                   purchase.quantity,
                                   datetime_to_string(purchase.purchase_datetime)], 1)
        self.purchases.append(purchase)
