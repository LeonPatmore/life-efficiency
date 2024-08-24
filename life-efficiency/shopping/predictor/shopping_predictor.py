from datetime import timedelta, datetime

from shopping.history.shopping_item_purchase import ShoppingItemPurchase


class ShoppingPredictor(object):

    def __init__(self,
                 purchases: list[ShoppingItemPurchase],
                 current_timestamp: datetime,
                 buy_buffer_days: int = 1):
        self.purchases = purchases
        self.current_timestamp = current_timestamp
        self.buy_buffer_days = buy_buffer_days

    def _get_today_with_buffer(self):
        return self.current_timestamp + timedelta(days=self.buy_buffer_days)

    def get_purchases_for_item(self, item) -> list[ShoppingItemPurchase]:
        purchases_for_item = [x for x in self.purchases if x.name.lower() == item.lower()]
        purchases_for_item.sort(key=lambda x: x.date.timestamp())
        return purchases_for_item

    def get_average_buy_difference_timestamp(self, item: str) -> timedelta or None:
        purchases_for_item = self.get_purchases_for_item(item)
        if len(purchases_for_item) < 2:
            return None
        total_range = purchases_for_item[-1].date.timestamp() - purchases_for_item[0].date.timestamp()
        total_quantity = sum([x.quantity for x in purchases_for_item])
        return total_range / (total_quantity - 1)

    def should_buy_today(self, item: str) -> bool:
        purchases_for_item = self.get_purchases_for_item(item)
        if len(purchases_for_item) < 2:
            return False
        avg_buy_difference_timestamp = self.get_average_buy_difference_timestamp(item)
        return purchases_for_item[-1].date.timestamp() + avg_buy_difference_timestamp <= \
            self._get_today_with_buffer().timestamp()

    def time_since_last_bought(self, item: str) -> timedelta or None:
        purchases_for_item = self.get_purchases_for_item(item)
        if len(purchases_for_item) < 1:
            return None
        return self.current_timestamp - purchases_for_item[-1].date
