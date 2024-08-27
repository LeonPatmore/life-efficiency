from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget
from lambda_splitter.response_handler import JsonResponseHandler
from lambda_splitter.validators import JsonBodyValidator, QueryParamValidator, TypedField
from shopping.history.shopping_history import ShoppingItemPurchase
from shopping.repeatingitems.shopping_repeating_items import RepeatingItem
from shopping.shopping_manager import ShoppingManager


QUANTITY_FIELD = TypedField("quantity", int)


class ShoppingHandler(LambdaSplitter):

    def __init__(self, shopping_manager: ShoppingManager):
        super().__init__("subcommand")
        self.shopping_manager = shopping_manager

        self.add_sub_handler('history', LambdaTarget(self.shopping_manager.shopping_history.get_all,
                                                     response_handler=JsonResponseHandler()))
        self.add_sub_handler('history',
                             LambdaTarget(lambda fields: self.shopping_manager.shopping_history.add(
                                 ShoppingItemPurchase(fields["name"], fields["quantity"])),
                                          [JsonBodyValidator(["name", QUANTITY_FIELD])]),
                             'POST')
        self.add_sub_handler('list', LambdaTarget(self.shopping_manager.shopping_list.get_all,
                                                  response_handler=JsonResponseHandler()))
        self.add_sub_handler('list',
                             LambdaTarget(lambda fields: self.shopping_manager.shopping_list.increase_quantity(
                                 fields["name"], fields["quantity"]), [JsonBodyValidator(["name", QUANTITY_FIELD])]),
                             'POST')
        self.add_sub_handler('list',
                             LambdaTarget(lambda fields: self.shopping_manager.shopping_list.reduce_quantity(
                                 fields["name"], fields["quantity"]), [QueryParamValidator(["name", QUANTITY_FIELD])]),
                             'DELETE')
        self.add_sub_handler('items',
                             LambdaTarget(lambda fields: self.shopping_manager.complete_items(fields['items']),
                                          [JsonBodyValidator([TypedField("items", list)])]),
                             'POST')
        self.add_sub_handler('today', LambdaTarget(self.shopping_manager.today_items,
                                                   response_handler=JsonResponseHandler()))
        self.add_sub_handler('today', LambdaTarget(self.shopping_manager.complete_today), 'POST')
        self.add_sub_handler('today',
                             LambdaTarget(lambda fields: self.shopping_manager.complete_item(
                                 fields["name"], fields["quantity"]), [QueryParamValidator(["name", QUANTITY_FIELD])]),
                             'DELETE')
        self.add_sub_handler('repeating', LambdaTarget(self.shopping_manager.repeating_items.get_all,
                                                       response_handler=JsonResponseHandler()))
        self.add_sub_handler('repeating',
                             LambdaTarget(lambda fields: self.shopping_manager.repeating_items.add(RepeatingItem(fields['item'])), [JsonBodyValidator(["item"])]),
                             'POST')
        self.add_sub_handler('repeating-details', LambdaTarget(self.shopping_manager.repeating_item_predictor,
                                                               response_handler=JsonResponseHandler()))
