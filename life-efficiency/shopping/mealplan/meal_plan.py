import logging
from datetime import datetime


class MealPlan:

    def __init__(self, items: list):
        self.items = items


class MealPlanService:

    def __init__(self, time_provider: callable):
        self.time_provider = time_provider
        self.meal_plans = self._load_meal_plans()
        logging.info(f"Meal plan has a cycle time of [ {len(self.meal_plans)} ]")
        self.current_cycle_start_time = self._get_current_cycle_start_time()

    def get_meal_plan_of_current_day_plus_offset(self, day_offset: int = 0) -> MealPlan:
        return self.meal_plans[self._get_day_index(day_offset)]

    def is_meal_plan_of_current_day_plus_offset_purchased(self, day_offset: int = 0):
        return self._is_meal_purchased(self._get_day_index(day_offset))

    def purchase_meal_plan_of_current_day_plus_offset(self, day_offset: int = 0):
        self._set_meal_purchased(self._get_day_index(day_offset), True)

    def _get_day_index(self, day_offset: int) -> int:
        if day_offset >= len(self.meal_plans):
            raise ValueError("Day offset must not be larger than the number of meal plans")
        time_diff = self.time_provider() - self.current_cycle_start_time
        logging.info(f"Current time diff is [ {time_diff.days} ] days!")
        day_index = time_diff.days + day_offset
        if day_index >= len(self.meal_plans):
            self._reset_cycle()
            return self._get_day_index(day_offset)
        return day_index

    def _reset_cycle(self):
        logging.info("Resetting meal plan cycle")
        self.current_cycle_start_time = self.time_provider()
        self._set_current_cycle_start_time(self.current_cycle_start_time)
        for i in range(len(self.meal_plans)):
            self._set_meal_purchased(i, False)

    def _load_meal_plans(self) -> list[MealPlan]:
        raise NotImplementedError()

    def _set_current_cycle_start_time(self, current_cycle_start_time: datetime):
        raise NotImplementedError()

    def _get_current_cycle_start_time(self) -> datetime:
        raise NotImplementedError()

    def _is_meal_purchased(self, index: int) -> bool:
        raise NotImplementedError()

    def _set_meal_purchased(self, index: int, purchased: bool):
        raise NotImplementedError()
