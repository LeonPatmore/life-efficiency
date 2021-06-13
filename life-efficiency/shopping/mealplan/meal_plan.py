import logging
import types
from datetime import datetime
from enum import Enum


class MealPlan(object):

    def __init__(self, time_provider: types.FunctionType, days: Enum, weeks: int):
        self.time_provider = time_provider  # A function that returns a datetime of the current time.
        self.days = days
        self.weeks = weeks
        self.mean_plan = dict()
        self._load_meal_plans()
        for i in range(weeks):
            self.mean_plan.setdefault(i, {})
            for _, day in enumerate(days):
                self.mean_plan[i].setdefault(day, [])

    def get_meal_for_day_and_week(self, day: Enum, week: int) -> list:
        week_plan = self.mean_plan.get(week)
        return week_plan.get(day, [])

    def _load_meal_plans(self):
        raise NotImplementedError()

    def _get_purchase_time(self) -> datetime:
        raise NotImplementedError()

    def _reset_purchase_time(self, new_time: datetime):
        raise NotImplementedError()

    def _is_meal_purchased_implementation(self, day: Enum, week: int) -> bool:
        raise NotImplementedError()

    def _purchase_meal_implementation(self, day: Enum, week: int):
        raise NotImplementedError()

    def is_meal_purchased(self, day: Enum, week: int):
        if week < 0 or week >= self.weeks:
            raise ValueError()
        self._check_purchase_time()
        return self._is_meal_purchased_implementation(day, week)

    def purchase_meal(self, day: Enum, week: int):
        if week < 0 or week >= self.weeks:
            raise ValueError()
        self._check_purchase_time()
        return self._purchase_meal_implementation(day, week)

    def _check_purchase_time(self):
        current_purchase_time = self._get_purchase_time()
        current_week = current_purchase_time.isocalendar()[1]
        today_week = self.time_provider().isocalendar()[1]

        logging.info("Current purchase week [ {}  ], today week [ {} ]", current_week, today_week)

        if today_week > current_week + self.weeks:
            logging.info("Resetting purchase time!")
            self._reset_purchase_time(self.time_provider())

    def get_current_week(self) -> int:
        raise NotImplementedError()
