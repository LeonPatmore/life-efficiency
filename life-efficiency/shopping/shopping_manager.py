import logging

from lambda_splitter.errors import HTTPAwareException
from shopping.history.shopping_history import ShoppingHistory, ShoppingItemPurchase
from shopping.ignore.shopping_ignore import ShoppingIgnore
from shopping.list.shopping_list import ShoppingList
from shopping.predictor.shopping_predictor import ShoppingPredictor
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems


class UnexpectedBuyException(HTTPAwareException):

    def __init__(self, item: str, quantity: int):
        super(UnexpectedBuyException, self).__init__(400, "Unexpected item {} of quantity {}".format(item, quantity))
        self.item = item
        self.quantity = quantity


class RemovedItems(object):

    def __init__(self, quantity: int, extra_removed_items: list = None):
        if extra_removed_items is None:
            extra_removed_items = list()
        self.quantity = quantity
        self.extra_removed_items = extra_removed_items


class ShoppingManager(object):

    def __init__(self,
                 shopping_history: ShoppingHistory,
                 shopping_list: ShoppingList,
                 repeating_items: RepeatingItems,
                 shopping_ignore: ShoppingIgnore,
                 current_timestamp_provider):
        self.current_timestamp_provider = current_timestamp_provider
        self.shopping_history = shopping_history
        self.shopping_list = shopping_list
        self.repeating_items = repeating_items
        self.shopping_ignore = shopping_ignore
        self.reduction_functions = [self._check_shopping_list]

    @staticmethod
    def _condense_extra_removed_items(extra_removed_items: list) -> list:
        condensed_items = []
        for item in extra_removed_items:
            if item not in [x[0] for x in condensed_items]:
                condensed_items.append([item, extra_removed_items.count(item)])
        return condensed_items

    def _check_shopping_list(self, item: str, quantity: int) -> RemovedItems:
        num = min(self.shopping_list.get_item_count(item), quantity)
        self.shopping_list.reduce_quantity(item, num)
        return RemovedItems(num)

    def today_items(self) -> list[str]:
        shopping_predictor = ShoppingPredictor(self.shopping_history.get_all(),
                                               self.current_timestamp_provider())
        ignored = self.shopping_ignore.get_all_within_ttl()
        predicted_repeating_items = [x.id for x in self.repeating_items.get_all()
                                     if shopping_predictor.should_buy_today(x.id) and x.id not in ignored]

        shopping_list = []
        for list_item in self.shopping_list.get_all():
            for _ in range(list_item.quantity):
                shopping_list.append(list_item.id)
        logging.info(f"Todays items are made from predicted [ {predicted_repeating_items} ] and "
                     f"list [ {shopping_list} ]")
        return predicted_repeating_items + shopping_list

    def repeating_item_predictor(self) -> dict:
        shopping_predictor = ShoppingPredictor(self.shopping_history.get_all(),
                                               self.current_timestamp_provider())
        repeating_items = self.repeating_items.get_all()

        def get_delta_days_for_item(item: str) -> int or None:
            delta = shopping_predictor.get_average_buy_difference_timestamp(item)
            return round(delta / 86400.0) if delta else None

        def get_time_since_last_bought_days(item: str) -> int or None:
            delta = shopping_predictor.time_since_last_bought(item)
            return delta.days if delta else None
        return {
            x.id: {"avg_gap_days": get_delta_days_for_item(x.id),
                   "today": shopping_predictor.should_buy_today(x.id),
                   "time_since_last_bought": get_time_since_last_bought_days(x.id)}
            for x in repeating_items}

    def complete_item(self, item: str, quantity: int) -> list:
        extra_removed_items = []
        if not item.strip():
            logging.info("Skipping item since it is empty!")
            return extra_removed_items
        self.shopping_history.add(ShoppingItemPurchase(item, quantity))
        for quantity_reduction_function in self.reduction_functions:
            # noinspection PyArgumentList
            removed_items = quantity_reduction_function(item, quantity)  # type: RemovedItems
            quantity = quantity - removed_items.quantity
            logging.info(f"Completing [ {item} ] of quantity [ {quantity} ] "
                         f"has also removed items [ {removed_items.extra_removed_items} ]")
            extra_removed_items.extend(removed_items.extra_removed_items)
            if quantity <= 0:
                return extra_removed_items
        else:
            # If quantity is still left over, it must be a repeating item.
            if item not in self.repeating_items.get_all():
                raise UnexpectedBuyException(item, quantity)
            return extra_removed_items

    def complete_items(self, items: list):
        items_with_removed = [[x, False] for x in items]
        for item in items_with_removed:
            # Skip if already removed.
            if item[1]:
                continue

            # Remove item and mark as removed.
            extra_removed_items = self.complete_item(item[0], 1)
            item[1] = True

            logging.info(f"Extra removed items are [ {extra_removed_items} ]")

            # Try to remove all extra items from list.
            for extra_removed_item in extra_removed_items:
                extra_removed_item_name = extra_removed_item[0]
                extra_removed_item_quantity = extra_removed_item[1]
                for todays_item_with_removed in items_with_removed:
                    if extra_removed_item_quantity <= 0:
                        break
                    if todays_item_with_removed[0] == extra_removed_item_name:
                        todays_item_with_removed[1] = True
                        extra_removed_item_quantity = extra_removed_item_quantity - 1

                if extra_removed_item_quantity:
                    logging.warning("Maybe you missed buying [ {} ] of [ {} ]".format(extra_removed_item_quantity,
                                                                                      extra_removed_item_name))

    def complete_today(self):
        self.complete_items(self.today_items())
