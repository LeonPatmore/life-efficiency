import datetime
from itertools import groupby


class ShoppingListItem:

    def __init__(self,
                 name: str,
                 quantity: int,
                 date_added: datetime.datetime):
        self.name = name
        self.quantity = quantity
        self.date_added = date_added


class ShoppingList:

    def __init__(self, current_datetime_generator: callable):
        self.current_datetime_generator = current_datetime_generator

    def get_item(self, item_name: str) -> ShoppingListItem or None:
        return self.get_items_map().get(item_name, None)

    def get_item_count(self, item_name: str):
        item = self.get_item(item_name)
        return item.quantity if item is not None else 0

    def reduce_quantity(self, item_name: str, quantity: int):
        item = self.get_item(item_name)
        if item is None:
            return
        if quantity >= item.quantity:
            self.remove_item(item_name)
        else:
            self.set_item_quantity(item_name, item.quantity - quantity)

    def increase_quantity(self, item_name: str, quantity: int):
        item = self.get_item(item_name)
        if item is None:
            self.add_item(ShoppingListItem(item_name, quantity, self.current_datetime_generator()))
        else:
            self.set_item_quantity(item_name, quantity + item.quantity)

    def get_items_map(self) -> dict[str, ShoppingListItem]:
        items = self.get_items()
        return {item_name: ShoppingListItem(name=item_name,
                                            quantity=sum([x.quantity for x in item_list]),
                                            date_added=list(item_list)[0].date_added)
                for item_name, item_list in
                ((item_name, list(item_group))
                 for item_name, item_group in groupby(items, lambda x: x.name))}

    def get_items(self) -> list[ShoppingListItem]:
        raise NotImplementedError()

    def add_item(self, item: ShoppingListItem):
        raise NotImplementedError()

    def remove_item(self, item_name: str):
        raise NotImplementedError()

    def set_item_quantity(self, item_name: str, quantity: int):
        raise NotImplementedError()
