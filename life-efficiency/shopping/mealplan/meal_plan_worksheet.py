from datetime import datetime
from distutils.util import strtobool

import gspread

from helpers.datetime import Day, string_to_datetime, datetime_to_string, get_current_datetime_utc
from shopping.mealplan.meal_plan import MealPlan


class MealPlanWorksheet(MealPlan):

    def __init__(self, meal_plan_worksheet: gspread.Worksheet, meal_purchase_worksheet: gspread.Worksheet):
        self.meal_plan_worksheet = meal_plan_worksheet
        self.meal_purchase_worksheet = meal_purchase_worksheet
        super().__init__()
        self._init_worksheet()

    def _init_worksheet(self):
        if self.meal_purchase_worksheet.get_all_values()[0][0] == "":
            self._reset_purchase_time(get_current_datetime_utc())

    def _load_meal_plans(self):
        worksheet_values = self.meal_plan_worksheet.get_all_values()
        for index, day in enumerate(Day):
            worksheet_row = worksheet_values[index]
            self.mean_plan[day] = worksheet_row

    def _get_purchase_time(self) -> datetime:
        return string_to_datetime(self.meal_purchase_worksheet.get_all_values()[0][0])

    def _reset_purchase_time(self, new_time: datetime):
        self.meal_purchase_worksheet.update_cell(0, 0, datetime_to_string(new_time))
        for day in Day:
            self.meal_purchase_worksheet.update_cell(day.value + 1, 0, "False")

    def _is_meal_purchased_implementation(self, day: Day) -> bool:
        purchased_string = self.meal_purchase_worksheet.get_all_values()[day.value + 1][0]  # type: str
        return strtobool(purchased_string)

    def _purchase_meal_implementation(self, day: Day):
        self.meal_purchase_worksheet.update_cell(day.value + 1, 0, "True")
