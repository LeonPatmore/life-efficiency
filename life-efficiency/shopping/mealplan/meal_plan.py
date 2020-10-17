from helpers.datetime import Day


class MealPlan(object):

    def __init__(self):
        self.mean_plan = dict()

    def _load_meal_plans(self):
        raise NotImplementedError()

    def get_meal_for_day(self, day: Day) -> list:
        return self.mean_plan.get(day, [])

    def is_meal_purchased(self, day: Day) -> bool:
        raise NotImplementedError()

    def purchase_meal(self, day: Day):
        raise NotImplementedError()

    def add_meal(self, day: Day, items: list, append: bool = False):
        if append:
            self.mean_plan[day] = self.mean_plan.get(day, []) + items
        else:
            self.mean_plan[day] = items
