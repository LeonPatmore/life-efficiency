import json
from inspect import signature
from json import JSONDecodeError

from lambda_splitter.errors import HTTPAwareException
from lambda_splitter.response_handler import ResponseHandler
from lambda_splitter.validators import Validator

ANY_METHOD = "ANY"


class LambdaTarget:

    def __init__(self,
                 handler: object,
                 validators: list[Validator] or None = None,
                 response_handler: ResponseHandler or None = None):
        if validators is None:
            validators = []
        self.handler = handler
        self.validators = validators
        self.response_handler = response_handler


class LambdaSplitter(object):

    def __init__(self, path_parameter_key: str, path_index: int = 0):
        self.path_parameter_key = path_parameter_key
        self.path_index = path_index
        self.sub_handlers = dict()

    def add_sub_handler(self, sub_path: str, target: LambdaTarget, method: str = "GET"):
        sanitised_sub_path = self.sanitise_path(sub_path)
        if sanitised_sub_path not in self.sub_handlers:
            self.sub_handlers[sanitised_sub_path] = dict()
        sanitised_method = self.sanitise_method(method)
        self.sub_handlers[sanitised_sub_path][sanitised_method] = target

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

    def _handle_function(self, event, handler: callable, fields: dict) -> dict:
        kwargs = {}
        try:
            handler_params = list(signature(handler).parameters.keys())
            if 'params' in handler_params:
                kwargs['params'] = event['queryStringParameters'] \
                    if "queryStringParameters" in event and event["queryStringParameters"] is not None else {}
            if 'json' in handler_params:
                kwargs['json'] = json.loads(event['body'])
            if 'path' in handler_params:
                kwargs["path"] = event["path"]
            if 'fields' in handler_params:
                kwargs["fields"] = fields
        except Exception as e:
            return self._handle_json_exception(e)
        response = handler(**kwargs)
        if response is None:
            return {'statusCode': 200}
        return response

    @staticmethod
    def _handle_lambda_splitter(event, context, fields: dict, handler) -> dict:
        return handler(event, context, fields=fields)

    def __call__(self, event, context: dict = None, fields: dict = None, **kwargs) -> dict:
        if fields is None:
            fields = {}
        if context is None:
            context = {}
        try:
            target = self._determine_method(event)
            if not isinstance(target, LambdaTarget):
                raise RuntimeError("Target must be of type LambdaTarget")
            for validator in target.validators:
                fields = fields | validator.validate(event)
            handler = target.handler
            if issubclass(type(handler), LambdaSplitter):
                response_obj = self._handle_lambda_splitter(event, context, fields, handler)
            elif callable(handler):
                response_obj = self._handle_function(event, handler, fields)
            else:
                raise RuntimeError(f'Target handler [ {type(handler)} ] not of type '
                                   'LambdaSplitter or Callable!')
            if target.response_handler:
                return target.response_handler.handle(response_obj)
            return response_obj
        except HTTPAwareException as e:
            return {
                'statusCode': e.status_code,
                'body': json.dumps(e.get_body())
            }

    def _determine_method(self, event):
        sub_path = self.sanitise_path(event['pathParameters'][self.path_parameter_key])
        sub_path_root = sub_path.split("/")[self.path_index]
        if sub_path_root in self.sub_handlers:
            method = self.sanitise_method(event['httpMethod'])
            if method in self.sub_handlers[sub_path_root]:
                return self.sub_handlers[sub_path_root][method]
            if ANY_METHOD in self.sub_handlers[sub_path_root]:
                return self.sub_handlers[sub_path_root][ANY_METHOD]
            raise HTTPAwareException(405)
        else:
            raise HTTPAwareException(404, f"could not find path for this command, "
                                          f"possible paths are [ {', '.join(self.sub_handlers.keys())} ]")
