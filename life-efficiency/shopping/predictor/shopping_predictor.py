from shopping.history.shopping_history import ShoppingHistory
from shopping.shopping_items import ShoppingItems


class ShoppingPredictor(object):

    def __init__(self, shopping_history: ShoppingHistory):
        self.shopping_history = shopping_history

    def should_buy_today(self, item: ShoppingItems) -> bool:
        self.shopping_history.get_purchases_for_item(item)
        # TODO: Finish
        return True
