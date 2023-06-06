from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistory(object):

    def __init__(self):
        self.purchases = self._load_all_purchases()

    def _load_all_purchases(self) -> list[ShoppingItemPurchase]:
        raise NotImplementedError()

    def get_purchases_for_item(self, item: str) -> list[ShoppingItemPurchase]:
        return [x for x in self.purchases if x.name.lower() == item.lower()]

    def get_all_purchases(self) -> list:
        return self.purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        raise NotImplementedError()
