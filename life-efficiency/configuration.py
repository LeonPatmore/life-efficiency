import logging

import boto3

from goals.goals_lambda_handler import GoalsHandler
from goals.goals_manager_worksheet import GoalsManagerWorksheet
from helpers.datetime import get_current_datetime_utc
from helpers.worksheets import init_worksheet
from lambda_handler import LifeEfficiencyLambdaHandler
from shopping.mealplan.meal_plan_worksheet import MealPlanWorksheet
from shopping.repeatingitems.shopping_repeating_items_worksheet import RepeatingItemsWorksheet
from shopping.shopping_lambda_handlers import ShoppingHandler
from shopping.shopping_manager_spreadsheet import ShoppingManagerSpreadsheet
from spreadsheet.spreadsheet_client_loader import SpreadsheetLoaderAWS
from todo.todo_lambda_handler import TodoHandler
from todo.list.todo_list_manager_spreadsheet import TodoListManagerWorksheet
from todo.weekly.todo_weekly_manager_spreadsheet import TodoWeeklyManagerWorksheet

logging.root.setLevel(logging.INFO)

# Only load env in dev.
try:
    import dotenv
except ImportError:
    dotenv = None
if dotenv:
    dotenv.load_dotenv()

spreadsheet = SpreadsheetLoaderAWS(boto3.client("s3"), boto3.client("secretsmanager")).spreadsheet
mean_plan = MealPlanWorksheet(get_current_datetime_utc,
                              init_worksheet(spreadsheet, "MealPlan"),
                              init_worksheet(spreadsheet, "MealPurchase"))
repeating_items = RepeatingItemsWorksheet(init_worksheet(spreadsheet, "RepeatingItems"))
shopping_manager = ShoppingManagerSpreadsheet(spreadsheet, mean_plan, repeating_items)
shopping_handler = ShoppingHandler(shopping_manager)

todo_list_manager = TodoListManagerWorksheet(init_worksheet(spreadsheet, "todo"), get_current_datetime_utc)
todo_weekly_manager = TodoWeeklyManagerWorksheet(init_worksheet(spreadsheet, "todo-weekly"), get_current_datetime_utc)
todo_handler = TodoHandler(todo_list_manager, todo_weekly_manager)

goals_manager = GoalsManagerWorksheet(init_worksheet(spreadsheet, "goals-manager"))
goals_handler = GoalsHandler(goals_manager)

handler = LifeEfficiencyLambdaHandler(shopping_handler=shopping_handler,
                                      todo_handler=todo_handler,
                                      goals_handler=goals_handler)
