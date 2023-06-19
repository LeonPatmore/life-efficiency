from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistory(object):

    def _load_all_purchases(self) -> list[ShoppingItemPurchase]:
        raise NotImplementedError()

    def get_purchases_for_item(self, item: str) -> list[ShoppingItemPurchase]:
        purchases = self._load_all_purchases()
        return [x for x in purchases if x.name.lower() == item.lower()]

    def get_all_purchases(self) -> list[ShoppingItemPurchase]:
        purchases = self._load_all_purchases()
        purchases.sort(key=lambda x: x.purchase_datetime.timestamp(), reverse=True)
        return purchases

    def add_purchase(self, purchase: ShoppingItemPurchase):
        raise NotImplementedError()
