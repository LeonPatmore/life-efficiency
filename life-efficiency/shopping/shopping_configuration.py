import logging

from configuration import spreadsheet, meal_plan_weeks
from helpers.datetime import Day, get_current_datetime_utc
from helpers.worksheets import init_worksheet
from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
from shopping.repeatingitems.shopping_repeating_items_worksheet import RepeatingItemsWorksheet
from shopping.shopping_manager_spreadsheet import ShoppingManagerSpreadsheet

logging.root.setLevel(logging.INFO)

mean_plan = MealPlanWorksheet(get_current_datetime_utc,
                              Day,
                              init_worksheet(spreadsheet, "MealPlan"),
                              init_worksheet(spreadsheet, "MealPurchase"),
                              meal_plan_weeks)
repeating_items = RepeatingItemsWorksheet(init_worksheet(spreadsheet, "RepeatingItems"))
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items, Day)
