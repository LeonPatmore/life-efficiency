from datetime import datetime

from helpers.datetime import get_current_datetime_utc


class ShoppingItemPurchase(object):

    def __init__(self, name: str, quantity: int, purchase_datetime: datetime = get_current_datetime_utc()):
        self.name = name.lower()
        self.quantity = quantity
        self.purchase_datetime = purchase_datetime

    def __str__(self):
        return "[ {} ] {} #{}".format(self.purchase_datetime, self.name, self.quantity)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "date": self.purchase_datetime
        }
