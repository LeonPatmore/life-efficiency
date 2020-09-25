import json


class LambdaSplitter(object):

    def __init__(self, path_parameter_key: str):
        self.path_parameter_key = path_parameter_key
        self.sub_handlers = dict()

    def add_sub_handler(self, sub_path, handler):
        self.sub_handlers[sub_path] = handler

    def __call__(self, event, context, **kwargs):
        sub_path = event['pathParameters'][self.path_parameter_key]
        if sub_path in self.sub_handlers:
            return self.sub_handlers[sub_path]()
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'could not find path for this command, possible paths are [ {} ]'
                    .format(', '.join(self.sub_handlers.keys()))
                })
            }
