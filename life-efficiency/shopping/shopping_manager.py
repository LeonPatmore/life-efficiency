import logging

from helpers.datetime import get_current_datetime_utc, Day
from helpers.lambda_splitter import HTTPAwareException
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.predictor.shopping_predictor import ShoppingPredictor


class UnexpectedBuyException(HTTPAwareException):

    def __init__(self, item: str, quantity: int):
        super(UnexpectedBuyException, self).__init__(400, "Unexpected item {} of quantity {}".format(item, quantity))
        self.item = item
        self.quantity = quantity


class RemovedItems(object):

    def __init__(self, quantity: int, extra_removed_items: list = list()):
        self.quantity = quantity
        self.extra_removed_items = extra_removed_items


class ShoppingManager(object):

    def __init__(self,
                 meal_plan,
                 shopping_history: ShoppingHistory,
                 shopping_list,
                 repeating_items):
        self.meal_plan = meal_plan
        self.shopping_history = shopping_history
        self.shopping_list = shopping_list
        self.shopping_predictor = ShoppingPredictor(shopping_history, get_current_datetime_utc)
        self.repeating_items = repeating_items

    def _get_quantity_reduction_items(self) -> list:

        def _check_shopping_list(item: str, quantity: int) -> RemovedItems:
            num = min(self.shopping_list.get_item_count(item), quantity)
            self.shopping_list.remove_item(item, num)
            return RemovedItems(num)

        def _check_meal_plan(item: str, quantity: int) -> RemovedItems:
            # TODO: This needs to be improved.
            for day in [Day((get_current_datetime_utc().weekday() + i) % 7) for i in range(7)]:
                if not self.meal_plan.is_meal_purchased(day):
                    todays_meal = self.meal_plan.get_meal_for_day(day)  # type: list
                    if item in todays_meal:
                        quantity_in_meal = min(quantity, todays_meal.count(item))
                        self.meal_plan.purchase_meal(day)
                        extra_removed_items = []
                        for an_item in todays_meal:
                            if item == an_item:
                                continue
                            if an_item in [x[0] for x in extra_removed_items]:
                                continue
                            an_item_count = todays_meal.count(an_item)
                            extra_removed_items.append((an_item, an_item_count))

                        return RemovedItems(quantity_in_meal, extra_removed_items)
            return 0

        return [_check_shopping_list, _check_meal_plan]

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items.get_repeating_items()
                                     if self.shopping_predictor.should_buy_today(x)]
        # TODO: Don't add to list if meal already bought!
        todays_meal = self.meal_plan.get_meal_for_day(Day(get_current_datetime_utc().weekday()))
        tomorrows_meal = self.meal_plan.get_meal_for_day(Day((get_current_datetime_utc().weekday() + 1) % 7))
        shopping_list = self.shopping_list.get_items()
        return predicted_repeating_items + todays_meal + tomorrows_meal + shopping_list

    def complete_item(self, item: str, quantity: int) -> list:
        extra_removed_items = []
        self.shopping_history.add_purchase(ShoppingItemPurchase(item, quantity))
        for quantity_reduction_function in self._get_quantity_reduction_items():
            removed_items = quantity_reduction_function(item, quantity)  # type: RemovedItems
            quantity = quantity - removed_items.quantity
            extra_removed_items.extend(removed_items.extra_removed_items)
            if quantity <= 0:
                return extra_removed_items

        else:
            # If quantity is still left over, it must be a repeating item.
            if item not in self.repeating_items.get_repeating_items():
                raise UnexpectedBuyException(item, quantity)

    def complete_today(self):
        todays_items_with_removed = [[x, False] for x in self.todays_items()]
        for item in todays_items_with_removed:
            # Skip if already removed.
            if item[1]:
                continue

            # Remove item and mark as removed.
            extra_removed_items = self.complete_item(item[0], 1)
            item[1] = True

            # Try to remove all extra items from list.
            for extra_removed_item in extra_removed_items:
                extra_removed_item_name = extra_removed_item[0]
                extra_removed_item_quantity = extra_removed_item[1]
                for todays_item_with_removed in todays_items_with_removed:
                    if extra_removed_item_quantity <= 0:
                        break
                    if todays_item_with_removed[0] == extra_removed_item_name:
                        todays_item_with_removed[1] = True
                        extra_removed_item_quantity = extra_removed_item_quantity - 1

                if extra_removed_item_quantity:
                    logging.warning("Maybe you missed buying [ {} ] of [ {} ]".format(extra_removed_item_quantity,
                                                                                      extra_removed_item_name))
