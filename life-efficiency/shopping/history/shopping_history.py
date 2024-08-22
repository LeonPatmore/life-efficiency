from repository.repository import Repository
from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingHistory(Repository[ShoppingItemPurchase]):

    def __init__(self):
        super().__init__(ShoppingItemPurchase)

    def get_all_sorted(self) -> list[ShoppingItemPurchase]:
        purchases = self.get_all()
        purchases.sort(key=lambda x: x.purchase_datetime.timestamp(), reverse=True)
        return purchases
