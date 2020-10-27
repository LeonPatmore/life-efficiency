from gspread import Spreadsheet

from helpers.datetime import get_current_datetime_utc, Day
from helpers.worksheets import init_worksheet
from shopping.history.shopping_history import ShoppingHistory
from shopping.history.shopping_history_worksheet import ShoppingHistoryWorksheet
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.list.shopping_list_worksheet import ShoppingListWorksheet
from shopping.predictor.shopping_predictor import ShoppingPredictor


class ShoppingManager(object):

    def __init__(self,
                 meal_plan,
                 shopping_history: ShoppingHistory,
                 shopping_list,
                 repeating_items: list):
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
            # TODO: Check to see if any un-purchased meal matches this item.
            pass

        return [_check_shopping_list, _check_meal_plan]

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items if self.shopping_predictor.should_buy_today(x)]
        todays_meal = self.meal_plan.get_meal_for_day(Day(get_current_datetime_utc().weekday()))
        tomorrows_meal = self.meal_plan.get_meal_for_day(Day((get_current_datetime_utc().weekday() + 1) % 7))
        list = self.shopping_list.get_items()
        return predicted_repeating_items + todays_meal + tomorrows_meal + list

    def complete_item(self, item: str, quantity: int):
        self.shopping_history.add_purchase(ShoppingItemPurchase(item, quantity))
        for quantity_reduction_function in self._get_quantity_reduction_items():
            quantity_taken = quantity_reduction_function(item, quantity)
            quantity = quantity - quantity_taken
        else:
            # TODO: There is still some quantity left over, so it must be a repeating item otherwise a mistake?
            pass

    def complete_today(self):
        for item in self.todays_items():
            self.complete_item(item, 1)


# TODO: Split into new file.
class ShoppingManagerSpreadsheet(ShoppingManager):

    def __init__(self, spreadsheet: Spreadsheet, meal_plan, repeating_items: list):
        shopping_history_worksheet = ShoppingHistoryWorksheet(init_worksheet(spreadsheet, "History"))
        shopping_list_worksheet = ShoppingListWorksheet(init_worksheet(spreadsheet, "List"))
        super(ShoppingManagerSpreadsheet, self).__init__(meal_plan,
                                                         shopping_history_worksheet,
                                                         shopping_list_worksheet,
                                                         repeating_items)
