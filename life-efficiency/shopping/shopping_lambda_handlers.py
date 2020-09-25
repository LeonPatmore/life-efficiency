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


shopping_handler = LambdaSplitter('subcommand')
shopping_handler.add_sub_handler('history', get_history)
