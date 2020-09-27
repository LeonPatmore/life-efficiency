from datetime import timedelta

from shopping.history.shopping_history import ShoppingHistory
from shopping.shopping_items import ShoppingItems


class ShoppingPredictor(object):

    def __init__(self,
                 shopping_history: ShoppingHistory,
                 current_timestamp_provider: callable,
                 buy_buffer_days: int = 1):
        self.shopping_history = shopping_history
        self.current_timestamp_provider = current_timestamp_provider
        self.buy_buffer_days = buy_buffer_days

    def _get_today_with_buffer(self):
        return self.current_timestamp_provider() + timedelta(days=self.buy_buffer_days)

    def should_buy_today(self, item: ShoppingItems) -> bool:
        purchases = self.shopping_history.get_purchases_for_item(item)
        if len(purchases) < 2:
            return False
        purchases.sort(key=lambda x: x.purchase_datetime.timestamp())
        total_range = purchases[-1].purchase_datetime.timestamp() - purchases[0].purchase_datetime.timestamp()
        total_quantity = sum([x.quantity for x in purchases])
        avg_buy_difference_timestamp = total_range / (total_quantity - 1)
        return purchases[-1].purchase_datetime.timestamp() + avg_buy_difference_timestamp <= \
            self._get_today_with_buffer().timestamp()
