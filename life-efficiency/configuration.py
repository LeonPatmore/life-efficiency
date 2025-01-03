import logging
import os

import boto3

from dynamo import dynamo_repository
from dynamo.dynamo_helpers import get_table_full_name
from dynamo.dynamo_repository import DynamoRepository
from finance.balance_change_manager import BalanceChangeManager
from finance.balance_instance_manager import BalanceInstanceManager
from finance.finance_manager import FinanceManager
from finance.finance_manager_handler import FinanceHandler, FinanceGraphHandler
from finance.metadata.finance_metadata_s3_loader import FinanceMetadataS3Loader
from goals.goals_lambda_handler import GoalsHandler
from goals.goals_manager import GoalsManager
from helpers.datetime import get_current_datetime_utc
from lambda_handler import LifeEfficiencyLambdaHandler
from repository import repository
from shopping.history.shopping_history import ShoppingHistory
from shopping.ignore.shopping_ignore import ShoppingIgnore
from shopping.list.shopping_list import ShoppingList
from shopping.repeatingitems.shopping_repeating_items import RepeatingItems
from shopping.shopping_lambda_handlers import ShoppingHandler
from shopping.shopping_manager import ShoppingManager
from todo.list.todo_list_manager import TodoListManager
from todo.todo_lambda_handler import TodoHandler
from todo.weekly.todo_weekly_manager_dynamo import TodoWeeklyManagerDynamo
from uploader.s3_uploader import S3Uploader

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

dynamodb = boto3.resource('dynamodb', **AWS_CLIENT_KWARGS)
dynamo_repository.table_generator = lambda name: dynamodb.Table(get_table_full_name(name))
repository.repository_implementation = DynamoRepository

s3_client = boto3.client('s3')
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
logging.info(f"Using bucket name [ {S3_BUCKET_NAME} ]")
FINANCE_METADATA_LOADER = FinanceMetadataS3Loader(s3_client, S3_BUCKET_NAME)
file_uploader = S3Uploader(s3_client, S3_BUCKET_NAME)

shopping_list = ShoppingList(get_current_datetime_utc)
repeating_items = RepeatingItems()
shopping_history = ShoppingHistory()
todo_list_manager = TodoListManager(get_current_datetime_utc)
todo_weekly_manager = TodoWeeklyManagerDynamo(dynamodb.Table(get_table_full_name("weekly-todos")),
                                              dynamodb.Table(get_table_full_name("todo-sets")),
                                              get_current_datetime_utc)
goals_manager = GoalsManager()
shopping_ignore = ShoppingIgnore()

shopping_manager = ShoppingManager(shopping_history,
                                   shopping_list,
                                   repeating_items,
                                   shopping_ignore,
                                   get_current_datetime_utc)
shopping_handler = ShoppingHandler(shopping_manager)
todo_handler = TodoHandler(todo_list_manager, todo_weekly_manager)
goals_handler = GoalsHandler(goals_manager)

finance_manager = FinanceManager(date_generator=get_current_datetime_utc,
                                 balance_instance_manager=BalanceInstanceManager(get_current_datetime_utc),
                                 balance_change_manager=BalanceChangeManager(get_current_datetime_utc),
                                 metadata_loader=FINANCE_METADATA_LOADER)
graph_handler = FinanceGraphHandler(finance_manager=finance_manager, file_uploader=file_uploader)
finance_handler = FinanceHandler(finance_manager=finance_manager, graph_handler=graph_handler)

handler = LifeEfficiencyLambdaHandler(shopping_handler=shopping_handler,
                                      todo_handler=todo_handler,
                                      goals_handler=goals_handler,
                                      finance_handler=finance_handler)
