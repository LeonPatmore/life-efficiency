from unittest.mock import Mock

import pytest

from helpers.lambda_splitter import LambdaSplitter

PATH_PARAMETER_KEY = 'path_parameter'


def _generate_event(path_parameter: str, sub_path: str) -> dict:
    return {
        'httpMethod': 'GET',
        'pathParameters': {
            path_parameter: sub_path
        }
    }


@pytest.fixture
def setup_lambda_splitter_with_method_handler():
    return_value = {'statusCode': 200}
    mock_method = Mock(return_value=return_value)

    def handler_method(*args, **kwargs): return mock_method(*args, **kwargs)
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    sub_path = 'sub_path'
    lambda_splitter.add_sub_handler(sub_path, handler_method)
    return lambda_splitter, mock_method, return_value, sub_path


_setup_lambda_splitter_with_method_handler = setup_lambda_splitter_with_method_handler


def test_sanitise_path_leading_slash():
    some_path = '/hello/bye'

    sanitised_path = LambdaSplitter.sanitise_path(some_path)

    assert sanitised_path == 'hello/bye'


def test_sanitise_path_ending_slash():
    some_path = 'hello/bye/'

    sanitised_path = LambdaSplitter.sanitise_path(some_path)

    assert sanitised_path == 'hello/bye'


def test_sanitise_method():
    some_method = 'gEt'

    sanitised_method = LambdaSplitter.sanitise_method(some_method)

    assert sanitised_method == 'GET'


def test_call_when_handler_is_a_method(_setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = _setup_lambda_splitter_with_method_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path), {})

    mock_method.assert_called_once_with()
    assert result == return_value


def test_call_when_no_subpath_match(_setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = _setup_lambda_splitter_with_method_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, 'unknown_path'), {})

    mock_method.assert_not_called()

    assert 'statusCode' in result
    assert result['statusCode'] == 404
    assert 'body' in result
    assert result['body'] == "{{\"error\": \"could not find path for this command, possible paths are [ {} ]\"}}"\
        .format(sub_path)


# def test_call_when_handler_is_a_lambda_splitter(_setup_lambda_splitter_with_method_handler):
#     lambda_splitter, mock_method, return_value, sub_path = _setup_lambda_splitter_with_method_handler
#
#     lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path), {})
#
#     mock_method.assert_called_once_with()
