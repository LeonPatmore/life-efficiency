import uuid

from helpers.datetime import datetime_to_string, string_to_datetime
from shopping.list.shopping_list import ShoppingList, ShoppingListItem


class ShoppingListDynamo(ShoppingList):

    def __init__(self, table, current_datetime_generator: callable):
        super().__init__(current_datetime_generator)
        self.table = table

    def get_items(self) -> list[ShoppingListItem]:
        return [ShoppingListItem(x["Name"], int(x["Quantity"]), string_to_datetime(x["DateAdded"]))
                for x in self.table.scan()["Items"]]

    def add_item(self, item: ShoppingListItem):
        self.table.put_item(Item={"Id": str(uuid.uuid4()),
                                  "Name": item.name,
                                  "Quantity": item.quantity,
                                  "DateAdded": datetime_to_string(item.date_added)})

    def remove_item(self, item_name: str):
        pass

    def set_item_quantity(self, item_name: str, quantity: int):
        pass
