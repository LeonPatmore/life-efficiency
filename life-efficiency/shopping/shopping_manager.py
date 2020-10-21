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

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items if self.shopping_predictor.should_buy_today(x)]
        todays_meal = self.meal_plan.get_meal_for_day(Day(get_current_datetime_utc().weekday()))
        tomorrows_meal = self.meal_plan.get_meal_for_day(Day((get_current_datetime_utc().weekday() + 1) % 7))
        return predicted_repeating_items + todays_meal + tomorrows_meal

    def complete_today(self):
        # TODO: Come up with a way to accept items for meal plan and list, as-well as repeating items.
        for item in self.todays_items():
            self.shopping_history.add_purchase(ShoppingItemPurchase(item, 1))


class ShoppingManagerSpreadsheet(ShoppingManager):

    def __init__(self, spreadsheet: Spreadsheet, meal_plan, repeating_items: list):
        shopping_history_worksheet = ShoppingHistoryWorksheet(init_worksheet(spreadsheet, "History"))
        shopping_list_worksheet = ShoppingListWorksheet(init_worksheet(spreadsheet, "List"))
        super(ShoppingManagerSpreadsheet, self).__init__(meal_plan,
                                                         shopping_history_worksheet,
                                                         shopping_list_worksheet,
                                                         repeating_items)
