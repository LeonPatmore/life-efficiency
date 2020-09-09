from shopping.shopping_items import ShoppingItems


class ShoppingHistory(object):

    def __init__(self):
        self.purchases = []
        raise NotImplementedError()

    def get_purchases_for_item(self, item: ShoppingItems):
        return [x for x in self.purchases if x.item == item]
