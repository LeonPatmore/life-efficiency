import gspread

from helpers.datetime import Day
from shopping.mealplan.meal_plan import MealPlan


class MealPlanWorksheet(MealPlan):

    def __init__(self, meal_plan_worksheet: gspread.Worksheet, meal_purchase_worksheet: gspread.Worksheet):
        self.meal_plan_worksheet = meal_plan_worksheet
        self.meal_purchase_worksheet = meal_purchase_worksheet
        self.meal_plans = dict()

    def _load_meal_plans(self):
        worksheet_values = self.meal_plan_worksheet.get_all_values()
        for index, day in enumerate(Day):
            worksheet_row = worksheet_values[index]
            self.meal_plans[day] = worksheet_row

    def is_meal_purchased(self, day: Day) -> bool:
        pass

    def purchase_meal(self, day: Day):
        pass
