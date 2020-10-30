import json

from helpers.datetime import get_current_datetime_utc
from helpers.lambda_splitter import LambdaSplitter, HTTPAwareException
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.shopping_configuration import shopping_manager


def get_history():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'purchases': [x.to_json() for x in shopping_manager.shopping_history.get_all_purchases()]
        }, default=str)
    }


def insert_purchase(json):
    item = json['item']
    try:
        quantity = int(json['quantity'])
    except ValueError:
        raise HTTPAwareException(400, 'quantity must be an integer')
    purchase = ShoppingItemPurchase(item, quantity)
    shopping_manager.shopping_history.add_purchase(purchase)


def get_list():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.shopping_list.get_items()
        }, default=str)
    }


def add_to_list(json):
    item = json['item']
    try:
        quantity = int(json['quantity'])
    except ValueError:
        raise HTTPAwareException(400, 'quantity must be an integer')
    shopping_manager.shopping_list.add_item(item, quantity, get_current_datetime_utc())


def get_today():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.todays_items()
        }, default=str)
    }


def complete_today():
    shopping_manager.complete_today()


shopping_handler = LambdaSplitter('subcommand')
shopping_handler.add_sub_handler('history', get_history)
shopping_handler.add_sub_handler('history', insert_purchase, 'POST')
shopping_handler.add_sub_handler('list', get_list)
shopping_handler.add_sub_handler('list', add_to_list, 'POST')
shopping_handler.add_sub_handler('today', get_today)
shopping_handler.add_sub_handler('today', complete_today, 'POST')
