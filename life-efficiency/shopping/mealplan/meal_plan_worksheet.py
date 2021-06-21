import logging
import types
from datetime import datetime
from distutils.util import strtobool
from enum import Enum

import gspread

from helpers.datetime import string_to_datetime, datetime_to_string
from shopping.mealplan.meal_plan import MealPlan


class MealPlanWorksheet(MealPlan):

    def __init__(self,
                 time_provider: types.FunctionType,
                 days: Enum,
                 meal_plan_worksheet: gspread.Worksheet,
                 meal_purchase_worksheet: gspread.Worksheet,
                 weeks: int):
        self.meal_plan_worksheet = meal_plan_worksheet
        self.meal_purchase_worksheet = meal_purchase_worksheet
        super().__init__(time_provider, days, weeks)
        self._init_worksheet()

    def _init_worksheet(self):
        worksheet_values = self.meal_purchase_worksheet.get_all_values()
        logging.info("Initing worksheet with initial values [ {} ]".format(worksheet_values))
        if not worksheet_values \
                or len(worksheet_values) == 0 \
                or len(worksheet_values[0]) == 0 \
                or worksheet_values[0][0] == "":
            self._reset_purchase_time(self.time_provider())

    def _load_meal_plans(self):
        worksheet_values = self.meal_plan_worksheet.get_all_values()
        for week in range(self.weeks):
            for day_index, day in enumerate(self.days):
                index = len(self.days) * week + day_index
                if index >= len(worksheet_values):
                    worksheet_row = []
                else:
                    worksheet_row = worksheet_values[index]
                self.mean_plan[week][day] = [x for x in worksheet_row if x.rstrip() != ""]

    def _get_purchase_time(self) -> datetime:
        return string_to_datetime(self.meal_purchase_worksheet.get_all_values()[0][0])

    def _reset_purchase_time(self, new_time: datetime):
        logging.info("Resetting purchase time for worksheet!")
        self.meal_purchase_worksheet.update_cell(1, 1, datetime_to_string(new_time))
        for week in range(self.weeks):
            for day in self.days:
                index = 2 + (len(self.days) * week) + day.value
                self.meal_purchase_worksheet.update_cell(index, 1, "False")

    def _is_meal_purchased_implementation(self, day, week) -> bool:
        index = week * len(self.days) + day.value + 1
        purchased_string = self.meal_purchase_worksheet.get_all_values()[index][0]  # type: str
        return strtobool(purchased_string)

    def _purchase_meal_implementation(self, day, week):
        index = week * len(self.days) + day.value + 2
        self.meal_purchase_worksheet.update_cell(index, 1, "True")
