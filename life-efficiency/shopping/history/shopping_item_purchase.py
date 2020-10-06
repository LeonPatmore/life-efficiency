from datetime import datetime

from helpers.datetime import get_current_datetime_utc


class ShoppingItemPurchase(object):
    """
    An shopping purchase.
    """

    def __init__(self, item: str, quantity: int, purchase_datetime: datetime = get_current_datetime_utc()):
        self.item = item.upper()
        self.quantity = quantity
        self.purchase_datetime = purchase_datetime

    def __str__(self):
        return "[ {} ] {} #{}".format(self.purchase_datetime, self.item, self.quantity)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return {
            "item": self.item,
            "quantity": self.quantity,
            "date": self.purchase_datetime
        }
