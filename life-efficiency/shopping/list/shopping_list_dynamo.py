from shopping.list.shopping_list import ShoppingList, ShoppingListItem


class ShoppingListDynamo(ShoppingList):

    def __init__(self, client):
        self.client = client

    def get_items(self) -> list[ShoppingListItem]:
        return self.client.scan(TableName=f"life-efficiency_local_spreadsheet-key")

    def add_item(self, item: ShoppingListItem):
        pass

    def remove_item(self, item_name: str):
        pass

    def set_item_quantity(self, item_name: str, quantity: int):
        pass
