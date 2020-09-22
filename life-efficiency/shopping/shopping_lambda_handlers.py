from shopping.shopping_configuration import shopping_manager


def get_history(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': str(shopping_manager.shopping_history.get_all_purchases())
    }
