from helpers.datetime import get_current_datetime_utc
from shopping.shopping_items import ShoppingItems
from datetime import datetime


class ShoppingItemPurchase(object):
    """
    An shopping purchase.
    """

    def __init__(self, item: ShoppingItems, quantity: int, purchase_datetime: datetime = get_current_datetime_utc()):
        self.item = item
        self.quantity = quantity
        self.purchase_datetime = purchase_datetime
