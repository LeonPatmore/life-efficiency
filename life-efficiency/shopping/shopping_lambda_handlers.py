import json

from helpers.datetime import get_current_datetime_utc
from helpers.lambda_splitter import LambdaSplitter, HTTPAwareException
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.shopping_configuration import shopping_manager


def validate_json_fields(json, required_fields=list()):
    for required_field in required_fields:
        if required_field not in json:
            raise HTTPAwareException(400, 'field `{}` is required'.format(required_field))


def get_history():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'purchases': [x.to_json() for x in shopping_manager.shopping_history.get_all_purchases()]
        }, default=str)
    }


def insert_purchase(json):
    validate_json_fields(json, ['item', 'quantity'])
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
            'items': [vars(x) for x in shopping_manager.shopping_list.get_items()]
        }, default=str)
    }


def add_to_list(json):
    validate_json_fields(json, ['name', 'quantity'])
    item_name = json['name']
    try:
        quantity = int(json['quantity'])
    except ValueError:
        raise HTTPAwareException(400, 'quantity must be an integer')
    shopping_manager.shopping_list.increase_quantity(item_name, quantity)


def get_today():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.todays_items()
        }, default=str)
    }


def complete_items(json):
    validate_json_fields(json, ['items'])
    shopping_manager.complete_items(json['items'])


def complete_today():
    shopping_manager.complete_today()


def get_repeating_items():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.repeating_items.get_repeating_items()
        }, default=str)
    }


def add_to_repeating_items(json):
    validate_json_fields(json, ['item'])
    shopping_manager.repeating_items.add_repeating_item(json['item'])


shopping_handler = LambdaSplitter('subcommand')
shopping_handler.add_sub_handler('history', get_history)
shopping_handler.add_sub_handler('history', insert_purchase, 'POST')
shopping_handler.add_sub_handler('list', get_list)
shopping_handler.add_sub_handler('list', add_to_list, 'POST')
shopping_handler.add_sub_handler('items', complete_items, 'POST')
shopping_handler.add_sub_handler('today', get_today)
shopping_handler.add_sub_handler('today', complete_today, 'POST')
shopping_handler.add_sub_handler('repeating', get_repeating_items)
shopping_handler.add_sub_handler('repeating', add_to_repeating_items, 'POST')
