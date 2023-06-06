import logging
from datetime import datetime
from distutils.util import strtobool

import gspread

from helpers.datetime import string_to_datetime, datetime_to_string
from shopping.mealplan.meal_plan import MealPlanService, MealPlan


class MealPlanWorksheet(MealPlanService):

    def __init__(self,
                 time_provider: callable,
                 meal_plan_worksheet: gspread.Worksheet,
                 meal_purchase_worksheet: gspread.Worksheet):
        self.meal_plan_worksheet = meal_plan_worksheet
        self.meal_purchase_worksheet = meal_purchase_worksheet
        super().__init__(time_provider)
        self._init_worksheet()

    def _init_worksheet(self):
        worksheet_values = self.meal_purchase_worksheet.get_all_values()
        logging.info(f"Meal purchase worksheet has initial values [ {worksheet_values} ]")
        if not worksheet_values \
                or len(worksheet_values) == 0 \
                or len(worksheet_values[0]) == 0 \
                or worksheet_values[0][0] == "":
            self._reset_cycle()

    def _load_meal_plans(self) -> list[MealPlan]:
        return [MealPlan([x for x in worksheet_row if x.rstrip() != ""])
                for worksheet_row in self.meal_plan_worksheet.get_all_values()
                if len(worksheet_row) > 0]

    def _set_current_cycle_start_time(self, current_cycle_start_time: datetime):
        self.meal_purchase_worksheet.update_cell(1, 1, datetime_to_string(current_cycle_start_time))

    def _get_current_cycle_start_time(self) -> datetime or None:
        try:
            return string_to_datetime(self.meal_purchase_worksheet.get("A1").first())
        except KeyError:
            return None

    def _is_meal_purchased(self, index: int) -> bool:
        purchased_string = self.meal_purchase_worksheet.get_all_values()[index + 1][0]
        return bool(strtobool(purchased_string))

    def _set_meal_purchased(self, index: int, purchased: bool):
        self.meal_purchase_worksheet.update_cell(index + 2, 1, str(purchased))
