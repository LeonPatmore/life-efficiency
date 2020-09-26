from gspread import Spreadsheet

from helpers.datetime import get_current_datetime_utc, Day
from helpers.worksheets import init_worksheet
from shopping.history.shopping_history import ShoppingHistoryWorksheet, ShoppingHistory
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.mealplan.mealplan import MealPlan
from shopping.predictor.shopping_predictor import ShoppingPredictor


class ShoppingManager(object):

    def __init__(self, meal_plan: MealPlan, shopping_history: ShoppingHistory, repeating_items: list):
        self.meal_plan = meal_plan
        self.shopping_history = shopping_history
        self.shopping_predictor = ShoppingPredictor(shopping_history)
        self.repeating_items = repeating_items

    def todays_items(self) -> list:
        predicted_repeating_items = [x for x in self.repeating_items if self.shopping_predictor.should_buy_today(x)]
        todays_meal = self.meal_plan.get_meal_for_day(Day(get_current_datetime_utc().weekday()))
        tomorrows_meal = self.meal_plan.get_meal_for_day(Day((get_current_datetime_utc().weekday() + 1) % 7))
        return predicted_repeating_items + todays_meal + tomorrows_meal

    def complete_today(self):
        for item in self.todays_items():
            self.shopping_history.add_purchase(ShoppingItemPurchase(item, 1))


class ShoppingManagerSpreadsheet(ShoppingManager):

    def __init__(self, spreadsheet: Spreadsheet, meal_plan: MealPlan, repeating_items: list):
        shopping_history_worksheet = ShoppingHistoryWorksheet(init_worksheet(spreadsheet, "History"))
        super(ShoppingManagerSpreadsheet, self).__init__(meal_plan, shopping_history_worksheet, repeating_items)
