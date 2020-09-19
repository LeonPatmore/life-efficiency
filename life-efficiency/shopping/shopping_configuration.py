from configuration import spreadsheet
from helpers.datetime import Day
from shopping.mealplan.mealplan import MealPlan
from shopping.shopping_items import ShoppingItems
from shopping.shopping_manager import ShoppingManagerSpreadsheet

repeating_items = [
    ShoppingItems.CHOCOLATE_MILKSHAKE,
    ShoppingItems.APPLES,
    ShoppingItems.GRAPES,
    ShoppingItems.PEARS,
    ShoppingItems.MOUTHWASH
]

mean_plan = MealPlan()
mean_plan.add_meal(Day.MONDAY, [ShoppingItems.PASTA, ShoppingItems.PESTO])
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items)
