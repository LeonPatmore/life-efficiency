import logging

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
                 repeating_items,
                 days,
                 current_timestamp_provider):
        self.current_timestamp_provider = current_timestamp_provider
        self.meal_plan = meal_plan
        self.shopping_history = shopping_history
        self.shopping_list = shopping_list
        self.shopping_predictor = ShoppingPredictor(shopping_history, current_timestamp_provider)
        self.repeating_items = repeating_items
        self.days = days

    @staticmethod
    def _check_if_item_can_be_removed_from_purchased_meal(item: str, quantity: int, meal: list):
        quantity_in_meal = meal.count(item)
        if item in meal and quantity_in_meal <= quantity:
            extra_items_to_remove = []
            for an_item in meal:
                if item == an_item:
                    continue
                extra_items_to_remove.append(an_item)
            return quantity_in_meal, extra_items_to_remove
        return 0, []

    @staticmethod
    def _condense_extra_removed_items(extra_removed_items: list) -> list:
        condensed_items = []
        for item in extra_removed_items:
            if item not in [x[0] for x in condensed_items]:
                condensed_items.append([item, extra_removed_items.count(item)])
        return condensed_items

    def _check_meal_plan(self, item: str, quantity: int) -> RemovedItems:
        # TODO: This needs to be improved.
        quantity_removed = 0
        extra_removed_items = []
        for week in range(self.meal_plan.get_current_week(), self.meal_plan.weeks):
            days_to_loop_in = self.meal_plan.days
            if week == self.meal_plan.get_current_week():
                days_to_loop_in = list(self.meal_plan.days)[self.current_timestamp_provider().weekday():]
            for day in days_to_loop_in:
                if not self.meal_plan.is_meal_purchased(day, week):
                    todays_meal = self.meal_plan.get_meal_for_day_and_week(day, week)  # type: list

                    quantity_in_meal, extra_items_to_remove = \
                        self._check_if_item_can_be_removed_from_purchased_meal(item, quantity, todays_meal)

                    if quantity_in_meal > 0:
                        self.meal_plan.purchase_meal(day, week)
                        extra_removed_items.extend(extra_items_to_remove)
                        quantity = quantity - quantity_in_meal
                        quantity_removed = quantity_removed + quantity_in_meal

        return RemovedItems(quantity_removed, self._condense_extra_removed_items(extra_removed_items))

    def _check_shopping_list(self, item: str, quantity: int) -> RemovedItems:
        num = min(self.shopping_list.get_item_count(item), quantity)
        self.shopping_list.reduce_quantity(item, num)
        return RemovedItems(num)

    def _get_quantity_reduction_items(self) -> list:
        return [self._check_shopping_list, self._check_meal_plan]

    def _meal_plan_items(self):

        todays_day = self.days(self.current_timestamp_provider().weekday() % len(self.days))
        this_week = self.meal_plan.get_current_week()
        logging.info("Today's day is [ {} ], week [ {} ]".format(todays_day, this_week))

        if not self.meal_plan.is_meal_purchased(todays_day, this_week):
            todays_meal = self.meal_plan.get_meal_for_day_and_week(todays_day, this_week)
        else:
            todays_meal = []

        tomorrows_day = self.days((self.current_timestamp_provider().weekday() + 1) % len(self.days))
        tomorrows_week = this_week
        if tomorrows_day.value <= todays_day.value:
            tomorrows_week = this_week + 1
        logging.info("Tomorrows's day is [ {} ], week [ {} ]".format(tomorrows_day, tomorrows_week))

        if not self.meal_plan.is_meal_purchased(tomorrows_day, tomorrows_week):
            tomorrows_meal = self.meal_plan.get_meal_for_day_and_week(tomorrows_day, tomorrows_week)
        else:
            tomorrows_meal = []

        return todays_meal + tomorrows_meal

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items.get_repeating_items()
                                     if self.shopping_predictor.should_buy_today(x)]
        meal_plan_meals = self._meal_plan_items()
        shopping_list = []
        for list_item in self.shopping_list.get_items():
            for _ in range(list_item.quantity):
                shopping_list.append(list_item.name)
        return predicted_repeating_items + meal_plan_meals + shopping_list

    def complete_item(self, item: str, quantity: int) -> list:
        extra_removed_items = []
        if not item.strip():
            logging.info("Skipping item since it is empty!")
            return extra_removed_items
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

    def complete_items(self, items: list):
        items_with_removed = [[x, False] for x in items]
        for item in items_with_removed:
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
        self.complete_items(self.todays_items())
