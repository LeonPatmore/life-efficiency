from configuration import spreadsheet
from helpers.datetime import Day
from helpers.worksheets import init_worksheet
from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
from shopping.shopping_items import CHOCOLATE_MILKSHAKE, APPLES, GRAPES, PEARS, MOUTHWASH, PASTA, PESTO, FISH, SALAD
from shopping.shopping_manager import ShoppingManagerSpreadsheet

repeating_items = [
    CHOCOLATE_MILKSHAKE,
    APPLES,
    GRAPES,
    PEARS,
    MOUTHWASH
]

mean_plan = MealPlanWorksheet(init_worksheet(spreadsheet, "MealPlan"), init_worksheet(spreadsheet, "MealPurchase"))
mean_plan.add_meal(Day.MONDAY, [PASTA, PESTO])
mean_plan.add_meal(Day.WEDNESDAY, [FISH, SALAD])
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items)
