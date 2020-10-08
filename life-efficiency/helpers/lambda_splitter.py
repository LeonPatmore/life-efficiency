import json
import types
from inspect import signature
from json import JSONDecodeError


class HTTPAwareException(Exception):

    def __init__(self,
                 status_code: int = 500,
                 error_message: str = None,
                 root_cause: Exception = None):
        self.root_cause = root_cause
        self.status_code = status_code
        self.error_message = error_message

    def get_body(self):
        if self.error_message:
            return {'error': self.error_message}
        elif self.root_cause:
            return {'error': 'exception during request processing',
                    'exception': self.root_cause}
        else:
            return {}


class LambdaSplitter(object):

    def __init__(self, path_parameter_key: str):
        self.path_parameter_key = path_parameter_key
        self.sub_handlers = dict()

    def add_sub_handler(self, sub_path: str, handler: object, method: str = "GET"):
        """
        Add a sub handler to this splitter.
        :param str sub_path: Sub path to match.
        :param types.FunctionType or LambdaSplitter handler: A handler. If it is a function, will call the function with
            no args. If it is a lambda splitter, will call the lambda splitter.
        :param str method: The method to match.
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

    @staticmethod
    def _handle_json_exception(exception: Exception) -> dict:
        if isinstance(exception, JSONDecodeError):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'body must be a valid JSON'
                })
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'error while trying to handle body',
                    'exception': str(exception)
                })
            }

    def _handle_function(self, event, handler: types.FunctionType) -> dict:
        kwargs = {}
        # JSON
        try:
            if 'json' in list(signature(handler).parameters.keys()):
                kwargs['json'] = json.loads(event['body'])
        except Exception as e:
            return self._handle_json_exception(e)
        response = handler(**kwargs)
        if not response:
            return {'statusCode': 200}
        return response

    @staticmethod
    def _handle_lambda_splitter(event, context, handler) -> dict:
        return handler(event, context)

    def __call__(self, event, context, **kwargs) -> dict:
        sub_path = self.sanitise_path(event['pathParameters'][self.path_parameter_key])
        if sub_path in self.sub_handlers:
            method = self.sanitise_method(event['httpMethod'])
            if method in self.sub_handlers[sub_path]:
                handler = self.sub_handlers[sub_path][method]
                try:
                    if isinstance(handler, types.FunctionType):
                        return self._handle_function(event, handler)
                    elif isinstance(handler, LambdaSplitter):
                        return self._handle_lambda_splitter(event, context, handler)
                    else:
                        raise RuntimeError('Handler not of expected type!')
                except HTTPAwareException as e:
                    return {
                        'statusCode': e.status_code,
                        'body': json.dumps(e.get_body())
                    }
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
