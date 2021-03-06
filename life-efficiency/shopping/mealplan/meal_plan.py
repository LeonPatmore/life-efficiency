import logging
import types
from datetime import datetime
from enum import Enum


class MealPlan(object):

    def __init__(self, time_provider: types.FunctionType, days: Enum):
        self.time_provider = time_provider  # A function that returns a datetime of the current time.
        self.days = days
        self.mean_plan = dict()
        self._load_meal_plans()

    def get_meal_for_day(self, day) -> list:
        list_of_items = self.mean_plan.get(day, [])
        return [x for x in list_of_items if x.rstrip() != ""]

    def _load_meal_plans(self):
        raise NotImplementedError()

    def _get_purchase_time(self) -> datetime:
        raise NotImplementedError()

    def _reset_purchase_time(self, new_time: datetime):
        raise NotImplementedError()

    def _is_meal_purchased_implementation(self, day) -> bool:
        raise NotImplementedError()

    def _purchase_meal_implementation(self, day):
        raise NotImplementedError()

    def is_meal_purchased(self, day):
        self._check_purchase_time()
        return self._is_meal_purchased_implementation(day)

    def purchase_meal(self, day):
        self._check_purchase_time()
        return self._purchase_meal_implementation(day)

    def _check_purchase_time(self):
        current_purchase_time = self._get_purchase_time()
        current_week = current_purchase_time.isocalendar()[1]
        today_week = self.time_provider().isocalendar()[1]

        logging.info("Current purchase week [ {}  ], today week [ {} ]", current_week, today_week)

        if current_week != today_week:
            logging.info("Resetting purchase time!")
            self._reset_purchase_time(self.time_provider())
