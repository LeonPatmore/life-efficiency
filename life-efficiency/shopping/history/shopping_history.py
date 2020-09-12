import logging
import gspread

from helpers.datetime import datetime_to_string, string_to_datetime
from shopping.shopping_item_purchase import ShoppingItemPurchase
from shopping.shopping_items import ShoppingItems


class ShoppingHistory(object):

    def __init__(self):
        self.purchases = self._load_all_purchases()  # type: list

    def _load_all_purchases(self):
        raise NotImplementedError()

    def get_purchases_for_item(self, item: ShoppingItems):
        return [x for x in self.purchases if x.item == item]

    def add_purchase(self, purchase: ShoppingItemPurchase):
        raise NotImplementedError()


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
                item = ShoppingItems[worksheet_row[0]]
                quantity = int(worksheet_row[1])
                datetime = string_to_datetime(worksheet_row[2])
                purchases.append(ShoppingItemPurchase(item, quantity, datetime))
            except Exception:
                logging.warning("Could not parse row, [ {} ]", worksheet_row)
        return purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.worksheet.insert_row([purchase.item.name,
                                   purchase.quantity,
                                   datetime_to_string(purchase.purchase_datetime)], 1)
        self.purchases.append(purchase)
