import json
import types


class LambdaSplitter(object):

    def __init__(self, path_parameter_key: str):
        self.path_parameter_key = path_parameter_key
        self.sub_handlers = dict()

    def add_sub_handler(self, sub_path: str, handler: object, method: str = "GET"):
        """

        :param sub_path:
        :param handler:
        :param method:
        :return:
        """
        sanitised_sub_path = self.sanitise_path(sub_path)
        if sanitised_sub_path not in self.sub_handlers:
            self.sub_handlers[sanitised_sub_path] = dict()
        sanitised_method = self.sanitise_method(method)
        self.sub_handlers[sanitised_sub_path][sanitised_method] = handler

    @staticmethod
    def sanitise_method(method: str) -> str:
        return method.upper()

    @staticmethod
    def sanitise_path(path: str) -> str:
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        return path

    def __call__(self, event, context, **kwargs):
        sub_path = self.sanitise_path(event['pathParameters'][self.path_parameter_key])
        if sub_path in self.sub_handlers:
            method = self.sanitise_method(event['httpMethod'])
            if method in self.sub_handlers[sub_path]:
                handler = self.sub_handlers[sub_path][method]
                if isinstance(handler, types.FunctionType):
                    return handler()
                elif isinstance(handler, LambdaSplitter):
                    return handler(event, context, **kwargs)
                else:
                    raise RuntimeError('Handler not of expected type!')
            else:
                return {'statusCode': 405}
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'could not find path for this command, possible paths are [ {} ]'
                    .format(', '.join(self.sub_handlers.keys()))
                })
            }
