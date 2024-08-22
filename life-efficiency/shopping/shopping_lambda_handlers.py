from lambda_splitter.errors import HTTPAwareException
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, QueryParamValidator, RequiredField
from shopping.history.shopping_item_purchase import ShoppingItemPurchase
from shopping.repeatingitems.shopping_repeating_items import RepeatingItem
from shopping.shopping_manager import ShoppingManager


QUANTITY_FIELD = RequiredField("quantity", int)


class ShoppingHandler(LambdaSplitter):

    def __init__(self, shopping_manager: ShoppingManager):
        super().__init__("subcommand")
        self.shopping_manager = shopping_manager

        self.add_sub_handler('history', LambdaTarget(self.shopping_manager.shopping_history.get_all,
                                                     response_handler=JsonResponseHandler()))
        self.add_sub_handler('history',
                             LambdaTarget(self.insert_purchase, [JsonBodyValidator(["name", QUANTITY_FIELD])]),
                             'POST')
        self.add_sub_handler('list', LambdaTarget(self.shopping_manager.shopping_list.get_all,
                                                  response_handler=JsonResponseHandler()))
        self.add_sub_handler('list',
                             LambdaTarget(self.add_to_list, [JsonBodyValidator(["name", QUANTITY_FIELD])]),
                             'POST')
        self.add_sub_handler('list',
                             LambdaTarget(self.delete_item, [QueryParamValidator(["name", QUANTITY_FIELD])]),
                             'DELETE')
        self.add_sub_handler('items',
                             LambdaTarget(self.complete_items, [JsonBodyValidator(["items"])]),
                             'POST')
        self.add_sub_handler('today', LambdaTarget(self.shopping_manager.today_items,
                                                   response_handler=JsonResponseHandler()))
        self.add_sub_handler('today', LambdaTarget(self.shopping_manager.complete_today), 'POST')
        self.add_sub_handler('today',
                             LambdaTarget(self.complete_item, [QueryParamValidator(["name", QUANTITY_FIELD])]),
                             'DELETE')
        self.add_sub_handler('repeating', LambdaTarget(self.shopping_manager.repeating_items.get_all,
                                                       response_handler=JsonResponseHandler()))
        self.add_sub_handler('repeating',
                             LambdaTarget(self.add_to_repeating_items, [JsonBodyValidator(["item"])]),
                             'POST')
        self.add_sub_handler('repeating-details', LambdaTarget(self.shopping_manager.repeating_item_predictor,
                                                               response_handler=JsonResponseHandler()))

    def insert_purchase(self, json):
        name = json['name']
        try:
            quantity = int(json['quantity'])
        except ValueError:
            raise HTTPAwareException(400, 'quantity must be an integer')
        purchase = ShoppingItemPurchase(name, quantity)
        self.shopping_manager.shopping_history.add(purchase)

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

    def complete_items(self, json):
        self.shopping_manager.complete_items(json['items'])

    def complete_item(self, params):
        item_name = params['name']
        item_quantity = int(params['quantity'])
        self.shopping_manager.complete_item(item_name, item_quantity)

    def add_to_repeating_items(self, json):
        self.shopping_manager.repeating_items.add(RepeatingItem(json['item']))
