from configuration import spreadsheet
from helpers.datetime import Day
from shopping.mealplan.mealplan import MealPlan
from shopping.shopping_items import CHOCOLATE_MILKSHAKE, APPLES, GRAPES, PEARS, MOUTHWASH, PASTA, PESTO
from shopping.shopping_manager import ShoppingManagerSpreadsheet

repeating_items = [
    CHOCOLATE_MILKSHAKE,
    APPLES,
    GRAPES,
    PEARS,
    MOUTHWASH
]

mean_plan = MealPlan()
mean_plan.add_meal(Day.MONDAY, [PASTA, PESTO])
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items)
