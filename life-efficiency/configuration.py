import logging
import os

import boto3

from dynamo.dynamo_helpers import get_table_full_name
from goals.goals_lambda_handler import GoalsHandler
from goals.goals_manager_dynamo import GoalsManagerDynamo
from goals.goals_manager_worksheet import GoalsManagerWorksheet
from helpers.datetime import get_current_datetime_utc
from helpers.worksheets import init_worksheet
from lambda_handler import LifeEfficiencyLambdaHandler
from shopping.history.shopping_history_dynamo import ShoppingHistoryDynamo
from shopping.history.shopping_history_worksheet import ShoppingHistoryWorksheet
from shopping.list.shopping_list_dynamo import ShoppingListDynamo
from shopping.list.shopping_list_worksheet import ShoppingListWorksheet
from shopping.repeatingitems.shopping_repeating_items_dynamo import RepeatingItemsDynamo
from shopping.repeatingitems.shopping_repeating_items_worksheet import RepeatingItemsWorksheet
from shopping.shopping_lambda_handlers import ShoppingHandler
from shopping.shopping_manager import ShoppingManager
from spreadsheet.spreadsheet_client_loader import SpreadsheetLoaderAWS
from todo.list.todo_list_manager_dynamo import TodoListManagerDynamo
from todo.list.todo_list_manager_spreadsheet import TodoListManagerWorksheet
from todo.todo_lambda_handler import TodoHandler
from todo.weekly.todo_weekly_manager_spreadsheet import TodoWeeklyManagerWorksheet

logging.root.setLevel(logging.INFO)

# Only load env in dev.
try:
    import dotenv
except ImportError:
    dotenv = None
if dotenv:
    dotenv.load_dotenv()

logging.info(os.environ)

AWS_CLIENT_KWARGS = {}
if os.environ.get("AWS_ENDPOINT_URL", None):
    logging.info(f"Using AWS endpoint {os.environ['AWS_ENDPOINT_URL']}")
    AWS_CLIENT_KWARGS["endpoint_url"] = os.environ["AWS_ENDPOINT_URL"]


backend = os.environ.get("BACKEND", "worksheets")
logging.info(f"Backend is {backend}")


if backend == "worksheets":
    spreadsheet = SpreadsheetLoaderAWS(boto3.client("s3"), boto3.client("secretsmanager")).spreadsheet
    repeating_items = RepeatingItemsWorksheet(init_worksheet(spreadsheet, "RepeatingItems"))
    shopping_history = ShoppingHistoryWorksheet(init_worksheet(spreadsheet, "History"))
    shopping_list = ShoppingListWorksheet(
        worksheet=init_worksheet(spreadsheet, "List"),
        current_datetime_generator=get_current_datetime_utc,
    )
    todo_list_manager = TodoListManagerWorksheet(init_worksheet(spreadsheet, "todo"), get_current_datetime_utc)
    todo_weekly_manager = TodoWeeklyManagerWorksheet(init_worksheet(spreadsheet, "todo-weekly"),
                                                     get_current_datetime_utc)
    goals_manager = GoalsManagerWorksheet(init_worksheet(spreadsheet, "goals-manager"))
else:
    dynamodb = boto3.resource('dynamodb', **AWS_CLIENT_KWARGS)
    shopping_list = ShoppingListDynamo(dynamodb.Table(get_table_full_name("shopping-list")), get_current_datetime_utc)
    repeating_items = RepeatingItemsDynamo(dynamodb.Table(get_table_full_name("repeating-items")))
    shopping_history = ShoppingHistoryDynamo(dynamodb.Table(get_table_full_name("shopping-history")))
    todo_list_manager = TodoListManagerDynamo(dynamodb.Table(get_table_full_name("todo-list")),
                                              get_current_datetime_utc)
    todo_weekly_manager = None
    goals_manager = GoalsManagerDynamo(dynamodb.Table(get_table_full_name("goals")))

shopping_manager = ShoppingManager(shopping_history,
                                   shopping_list,
                                   repeating_items,
                                   get_current_datetime_utc)
shopping_handler = ShoppingHandler(shopping_manager)
todo_handler = TodoHandler(todo_list_manager, todo_weekly_manager)
goals_handler = GoalsHandler(goals_manager)

handler = LifeEfficiencyLambdaHandler(shopping_handler=shopping_handler,
                                      todo_handler=todo_handler,
                                      goals_handler=goals_handler)
