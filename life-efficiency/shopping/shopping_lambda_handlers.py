import json

from lambda_splitter.errors import HTTPAwareException
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.validators import JsonBodyValidator, QueryParamValidator
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.shopping_manager import ShoppingManager


class ShoppingHandler(LambdaSplitter):

    def __init__(self, shopping_manager: ShoppingManager):
        super().__init__("subcommand")
        self.shopping_manager = shopping_manager

        self.add_sub_handler('history', LambdaTarget(self.get_history))
        self.add_sub_handler('history',
                             LambdaTarget(self.insert_purchase, [JsonBodyValidator(["name", "quantity"])]),
                             'POST')
        self.add_sub_handler('list', LambdaTarget(self.get_list))
        self.add_sub_handler('list',
                             LambdaTarget(self.add_to_list, [JsonBodyValidator(["name", "quantity"])]),
                             'POST')
        self.add_sub_handler('list',
                             LambdaTarget(self.delete_item, [QueryParamValidator(["name", "quantity"])]),
                             'DELETE')
        self.add_sub_handler('items',
                             LambdaTarget(self.complete_items, [JsonBodyValidator(["items"])]),
                             'POST')
        self.add_sub_handler('today', LambdaTarget(self.get_today))
        self.add_sub_handler('today', LambdaTarget(self.complete_today), 'POST')
        self.add_sub_handler('today',
                             LambdaTarget(self.complete_item, [QueryParamValidator(["name", "quantity"])]),
                             'DELETE')
        self.add_sub_handler('repeating', LambdaTarget(self.get_repeating_items))
        self.add_sub_handler('repeating',
                             LambdaTarget(self.add_to_repeating_items, [JsonBodyValidator(["item"])]),
                             'POST')
        self.add_sub_handler('repeating-details', LambdaTarget(self.get_repeating_details))

    def get_history(self):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'purchases': [x.to_json() for x in self.shopping_manager.shopping_history.get_all_purchases()]
            }, default=str)
        }

    def insert_purchase(self, json):
        name = json['name']
        try:
            quantity = int(json['quantity'])
        except ValueError:
            raise HTTPAwareException(400, 'quantity must be an integer')
        purchase = ShoppingItemPurchase(name, quantity)
        self.shopping_manager.shopping_history.add_purchase(purchase)

    def get_list(self):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'items': [vars(x) for x in self.shopping_manager.shopping_list.get_items()]
            }, default=str)
        }

    def add_to_list(self, json):
        item_name = json['name']
        try:
            quantity = int(json['quantity'])
        except ValueError:
            raise HTTPAwareException(400, 'quantity must be an integer')
        self.shopping_manager.shopping_list.increase_quantity(item_name, quantity)

    def delete_item(self, params):
        item_name = params['name']
        item_quantity = int(params['quantity'])
        self.shopping_manager.shopping_list.reduce_quantity(item_name, item_quantity)

    def get_today(self):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'items': self.shopping_manager.today_items()
            }, default=str)
        }

    def complete_items(self, json):
        self.shopping_manager.complete_items(json['items'])

    def complete_today(self):
        self.shopping_manager.complete_today()

    def complete_item(self, params):
        item_name = params['name']
        item_quantity = int(params['quantity'])
        self.shopping_manager.complete_item(item_name, item_quantity)

    def get_repeating_items(self):
        return {
            'statusCode': 200,
            'body': json.dumps({
                'items': self.shopping_manager.repeating_items.get_repeating_items()
            }, default=str)
        }

    def get_repeating_details(self):
        return {
            'statusCode': 200,
            'body': json.dumps(self.shopping_manager.repeating_item_predictor(), default=str)
        }

    def add_to_repeating_items(self, json):
        self.shopping_manager.repeating_items.add_repeating_item(json['item'])
