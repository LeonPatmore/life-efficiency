import json

from helpers.lambda_splitter import LambdaSplitter
from shopping.shopping_configuration import shopping_manager


def get_history():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'purchases': [x.to_json() for x in shopping_manager.shopping_history.get_all_purchases()]
        }, default=str)
    }


def get_today():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.todays_items()
        }, default=str)
    }


def complete_today():
    shopping_manager.complete_today()
    return {'statusCode': 200}


# def insert_purchase():
#     ShoppingItemPurchase()
#     shopping_manager.shopping_history.add_purchase()


shopping_handler = LambdaSplitter('subcommand')
shopping_handler.add_sub_handler('history', get_history)
shopping_handler.add_sub_handler('today', get_today)
shopping_handler.add_sub_handler('today', complete_today, 'POST')
