from configuration import spreadsheet
from helpers.datetime import Day, get_current_datetime_utc
from helpers.worksheets import init_worksheet
from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
from shopping.shopping_items import CHOCOLATE_MILKSHAKE, APPLES, GRAPES, PEARS, MOUTHWASH
from shopping.shopping_manager_spreadsheet import ShoppingManagerSpreadsheet

repeating_items = [
    CHOCOLATE_MILKSHAKE,
    APPLES,
    GRAPES,
    PEARS,
    MOUTHWASH
]

mean_plan = MealPlanWorksheet(get_current_datetime_utc,
                              Day,
                              init_worksheet(spreadsheet, "MealPlan"),
                              init_worksheet(spreadsheet, "MealPurchase"))
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items)
