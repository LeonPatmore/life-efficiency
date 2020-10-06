from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistory(object):

    def __init__(self):
        self.purchases = self._load_all_purchases()  # type: list

    def _load_all_purchases(self):
        raise NotImplementedError()

    def get_purchases_for_item(self, item: str) -> list:
        return [x for x in self.purchases if x.item.upper() == item.upper()]

    def get_all_purchases(self) -> list:
        return self.purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        raise NotImplementedError()
