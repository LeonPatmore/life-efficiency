from dataclasses import dataclass
from datetime import datetime

from dynamo.dynamo_repository import dynamo_item
from helpers.datetime import get_current_datetime_utc


@dynamo_item("shopping-history", {"Date": "purchase_datetime"})
@dataclass
class ShoppingItemPurchase(object):
    name: str
    quantity: int
    purchase_datetime: datetime = get_current_datetime_utc()
    id: str = None

    def __post_init__(self):
        self.name = self.name.strip().lower()

    def __str__(self):
        return "[ {} ] {} #{}".format(self.purchase_datetime, self.name, self.quantity)

    def __repr__(self):
        return self.__str__()
