from helpers.datetime import Day


class MealPlan(object):

    def __init__(self):
        self.mean_plan = dict()

    def get_meal_for_day(self, day: Day) -> list:
        return self.mean_plan.get(day, [])

    def add_meal(self, day: Day, items: list, append: bool = False):
        if append:
            self.mean_plan[day] = self.mean_plan.get(day, []) + items
        else:
            self.mean_plan[day] = items
