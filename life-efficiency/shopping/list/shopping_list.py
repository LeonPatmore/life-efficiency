from datetime import datetime


class ShoppingList(object):

    def get_items(self) -> list:
        raise NotImplementedError()

    def get_item_count(self, item: str):
        items = self.get_items()
        return items.count(item)

    def add_item(self, item: str, quantity: int, date_added: datetime):
        raise NotImplementedError()

    def remove_item(self, item: str, quantity: int):
        raise NotImplementedError()
