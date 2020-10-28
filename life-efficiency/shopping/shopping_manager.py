from helpers.datetime import get_current_datetime_utc, Day
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.predictor.shopping_predictor import ShoppingPredictor


class UnexpectedBuyException(Exception):

    def __init__(self, item: str, quantity: int):
        self.item = item
        self.quantity = quantity
        self.message = "Unexpected item {} of quantity {}".format(item, quantity)


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

        def _check_shopping_list(item: str, quantity: int) -> int:
            num = min(self.shopping_list.get_item_count(item), quantity)
            self.shopping_list.remove_item(item, num)
            return num

        def _check_meal_plan(item: str, quantity: int) -> int:
            # TODO: This needs to be improved.
            for day in [Day((get_current_datetime_utc().weekday() + i) % 7) for i in range(7)]:
                if not self.meal_plan.is_meal_purchased(day):
                    todays_meal = self.meal_plan.get_meal_for_day(day)  # type: list
                    if item in todays_meal:
                        quantity_in_meal = min(quantity, todays_meal.count(item))
                        self.meal_plan.purchase_meal(day)
                        return quantity_in_meal

        return [_check_shopping_list, _check_meal_plan]

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items.get_repeating_items()
                                     if self.shopping_predictor.should_buy_today(x)]
        todays_meal = self.meal_plan.get_meal_for_day(Day(get_current_datetime_utc().weekday()))
        tomorrows_meal = self.meal_plan.get_meal_for_day(Day((get_current_datetime_utc().weekday() + 1) % 7))
        shopping_list = self.shopping_list.get_items()
        return predicted_repeating_items + todays_meal + tomorrows_meal + shopping_list

    def complete_item(self, item: str, quantity: int):
        self.shopping_history.add_purchase(ShoppingItemPurchase(item, quantity))
        for quantity_reduction_function in self._get_quantity_reduction_items():
            quantity_taken = quantity_reduction_function(item, quantity)
            quantity = quantity - quantity_taken
            if quantity <= 0:
                break
        else:
            # If quantity is still left over, it must be a repeating item.
            if item not in self.repeating_items.get_repeating_items():
                raise UnexpectedBuyException(item, quantity)

    def complete_today(self):
        for item in self.todays_items():
            self.complete_item(item, 1)
