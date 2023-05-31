import json

from lambda_splitter.errors import HTTPAwareException
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.validators import JsonBodyValidator, QueryParamValidator
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
            'items': [vars(x) for x in shopping_manager.shopping_list.get_items()]
        }, default=str)
    }


def add_to_list(json):
    item_name = json['name']
    try:
        quantity = int(json['quantity'])
    except ValueError:
        raise HTTPAwareException(400, 'quantity must be an integer')
    shopping_manager.shopping_list.increase_quantity(item_name, quantity)


def delete_item(params):
    item_name = params['name']
    item_quantity = int(params['quantity'])
    shopping_manager.shopping_list.reduce_quantity(item_name, item_quantity)


def get_today():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.todays_items()
        }, default=str)
    }


def complete_items(json):
    shopping_manager.complete_items(json['items'])


def complete_today():
    shopping_manager.complete_today()


def complete_item(params):
    item_name = params['name']
    item_quantity = int(params['quantity'])
    shopping_manager.complete_item(item_name, item_quantity)


def get_repeating_items():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'items': shopping_manager.repeating_items.get_repeating_items()
        }, default=str)
    }


def add_to_repeating_items(json):
    shopping_manager.repeating_items.add_repeating_item(json['item'])


shopping_handler = LambdaSplitter('subcommand')
shopping_handler.add_sub_handler('history', LambdaTarget(get_history))
shopping_handler.add_sub_handler('history',
                                 LambdaTarget(insert_purchase, [JsonBodyValidator(["name", "quantity"])]),
                                 'POST')
shopping_handler.add_sub_handler('list', LambdaTarget(get_list))
shopping_handler.add_sub_handler('list',
                                 LambdaTarget(add_to_list, [JsonBodyValidator(["name", "quantity"])]),
                                 'POST')
shopping_handler.add_sub_handler('list',
                                 LambdaTarget(delete_item, [QueryParamValidator(["name", "quantity"])]),
                                 'DELETE')
shopping_handler.add_sub_handler('items',
                                 LambdaTarget(complete_items, [JsonBodyValidator(["items"])]),
                                 'POST')
shopping_handler.add_sub_handler('today', LambdaTarget(get_today))
shopping_handler.add_sub_handler('today', LambdaTarget(complete_today), 'POST')
shopping_handler.add_sub_handler('today',
                                 LambdaTarget(complete_item, [QueryParamValidator(["name", "quantity"])]),
                                 'DELETE')
shopping_handler.add_sub_handler('repeating', LambdaTarget(get_repeating_items))
shopping_handler.add_sub_handler('repeating',
                                 LambdaTarget(add_to_repeating_items, [JsonBodyValidator(["item"])]),
                                 'POST')
