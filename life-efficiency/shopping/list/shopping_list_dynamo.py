from shopping.list.shopping_list import ShoppingList, ShoppingListItem


class ShoppingListWorksheet(ShoppingList):

    def get_items(self) -> list[ShoppingListItem]:

    def add_item(self, item: ShoppingListItem):

    def remove_item(self, item_name: str):

    def set_item_quantity(self, item_name: str, quantity: int):
