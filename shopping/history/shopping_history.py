import logging
import gspread

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
                item = worksheet_row[0]
                quantity = worksheet_row[1]
                purchases.append(ShoppingItemPurchase(ShoppingItems[item], quantity))
            except Exception:
                logging.warning("Could not parse row, [ {} ]", worksheet_row)
        return purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.worksheet.insert_row([purchase.item.name, purchase.quantity], 1)
        self.purchases.append(purchase)
