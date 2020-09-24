import json

from shopping.shopping_configuration import shopping_manager


def get_history(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps({
            'purchases': [x.to_json() for x in shopping_manager.shopping_history.get_all_purchases()]
        }, default=str)
    }
