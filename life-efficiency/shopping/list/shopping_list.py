import datetime
import logging
from dataclasses import dataclass

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("shopping-list")
@dataclass
class ShoppingListItem:
    id: str
    quantity: int
    date_added: datetime.datetime

    def __post_init__(self):
        self.id = self.id.strip().lower()

    def to_json(self):
        return {
            "name": self.id,
            "quantity": self.quantity,
            "date_added": self.date_added
        }


class ShoppingList(Repository[ShoppingListItem]):

    def __init__(self, current_datetime_generator: callable):
        super().__init__(ShoppingListItem)
        self.current_datetime_generator = current_datetime_generator

    def set_item_quantity(self, item_id: str, quantity: int):
        self.update(item_id, "quantity", quantity)

    def get_item_count(self, item_name: str):
        item = self.get(item_name)
        return item.quantity if item is not None else 0

    def reduce_quantity(self, item_name: str, quantity: int):
        item = self.get(item_name)
        if item is None:
            logging.info(f"Reducing item [ {item_name} ] by quantity [ {quantity} ] "
                         f"will do nothing since item not present")
            return
        if quantity >= item.quantity:
            logging.info(f"Removing item [ {item_name} ] from shopping list")
            self.remove(item_name)
        else:
            new_quantity = item.quantity - quantity
            logging.info(f"Setting item [ {item_name} ] to quantity [ {new_quantity} ]")
            self.set_item_quantity(item_name, new_quantity)

    def increase_quantity(self, item_name: str, quantity: int):
        item = self.get(item_name)
        if item is None:
            logging.info(f"Adding item [ {item_name} ] with quantity [ {quantity} ]")
            self.add(ShoppingListItem(item_name, quantity, self.current_datetime_generator()))
        else:
            new_quantity = quantity + item.quantity
            logging.info(f"Setting item [ {item_name} ] to quantity [ {new_quantity} ]")
            self.set_item_quantity(item_name, new_quantity)
