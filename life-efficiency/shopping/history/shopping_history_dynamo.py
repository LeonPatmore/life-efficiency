from helpers.datetime import string_to_datetime, datetime_to_string
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistoryDynamo(ShoppingHistory):

    def __init__(self, table):
        self.table = table

    def _load_all_purchases(self) -> list:
        return [ShoppingItemPurchase(name=x["Id"],
                                     quantity=int(x["Quantity"]),
                                     purchase_datetime=string_to_datetime(x["Date"]))
                for x in self.table.scan()["Items"]]

    def add_purchase(self, purchase: ShoppingItemPurchase):
        self.table.put_item(Item={"Id": purchase.name,
                                  "Quantity": purchase.quantity,
                                  "Date": datetime_to_string(purchase.purchase_datetime)})
