from shopping.shopping_items import ShoppingItems


class ShoppingItemPurchase(object):
    """
    An shopping purchase.
    """

    def __init__(self, item: ShoppingItems, quantity: int):
        self.item = item
        self.quantity = quantity
