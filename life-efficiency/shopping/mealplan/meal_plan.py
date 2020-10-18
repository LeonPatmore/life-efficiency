import logging
from datetime import datetime

from helpers.datetime import Day, get_current_datetime_utc


class MealPlan(object):

    def __init__(self):
        self.mean_plan = dict()
        self._load_meal_plans()

    def get_meal_for_day(self, day: Day) -> list:
        return self.mean_plan.get(day, [])

    def _load_meal_plans(self):
        raise NotImplementedError()

    def _get_purchase_time(self) -> datetime:
        raise NotImplementedError()

    def _reset_purchase_time(self, new_time: datetime):
        raise NotImplementedError()

    def _is_meal_purchased_implementation(self, day: Day) -> bool:
        raise NotImplementedError()

    def _purchase_meal_implementation(self, day: Day):
        raise NotImplementedError()

    def is_meal_purchased(self, day: Day):
        self._check_purchase_time()
        return self._is_meal_purchased_implementation(day)

    def purchase_meal(self, day: Day):
        self._check_purchase_time()
        return self._purchase_meal_implementation(day)

    def _check_purchase_time(self):
        current_purchase_time = self._get_purchase_time()
        current_week = current_purchase_time.isocalendar()[1]
        today_week = get_current_datetime_utc().isocalendar()[1]

        logging.info("Current purchase week [ {} ], today week [ {} ]", current_week, today_week)

        if current_week != today_week:
            logging.info("Resetting purchase time!")
            self._reset_purchase_time(get_current_datetime_utc())

    def add_meal(self, day: Day, items: list, append: bool = False):
        if append:
            self.mean_plan[day] = self.mean_plan.get(day, []) + items
        else:
            self.mean_plan[day] = items
