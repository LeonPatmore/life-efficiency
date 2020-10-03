import json

from helpers.lambda_splitter import LambdaSplitter


def get_list():
    return {
        'statusCode': 200,
        'body': json.dumps({
            'todos': [x.to_json() for x in shopping_manager.shopping_history.get_all_purchases()]
        }, default=str)
    }


todo_handler = LambdaSplitter('subcommand')
todo_handler.add_sub_handler('list', get_history)
