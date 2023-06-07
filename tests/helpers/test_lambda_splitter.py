from unittest.mock import Mock

import pytest

from lambda_splitter.errors import HTTPAwareException
from lambda_splitter.lambda_splitter import LambdaSplitter, LambdaTarget

PATH_PARAMETER_KEY = 'path_parameter'

RESPONSE_STATUS_CODE_FIELD = 'statusCode'
RESPONSE_BODY_FIELD = 'body'

DEFAULT_SUB_PATH = "sub_path"
SUCCESS_MOCK = Mock(return_value={RESPONSE_STATUS_CODE_FIELD: 200})


def _generate_event(path_parameter: str, sub_path: str, body: str = None, method='GET') -> dict:
    return {
        'httpMethod': method,
        'pathParameters': {
            path_parameter: sub_path
        },
        'body': body
    }


def setup_lambda_splitter(lambda_target: LambdaTarget) -> LambdaSplitter:
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    lambda_splitter.add_sub_handler(DEFAULT_SUB_PATH, lambda_target)
    return lambda_splitter


@pytest.fixture
def setup_lambda_splitter_with_method_handler():
    return_value = {RESPONSE_STATUS_CODE_FIELD: 200}
    mock_method = Mock(return_value=return_value)

    def handler_method(*args, **kwargs): return mock_method(*args, **kwargs)
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    sub_path = 'sub_path'
    lambda_splitter.add_sub_handler(sub_path, LambdaTarget(handler_method))
    return lambda_splitter, mock_method, return_value, sub_path


@pytest.fixture
def setup_embedded_lambda_splitter(setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = setup_lambda_splitter_with_method_handler

    top_path_parameter_key = 'path_parameter_2'
    lambda_splitter_top = LambdaSplitter(top_path_parameter_key)
    top_sub_path = 'sub_path_2'
    lambda_splitter_top.add_sub_handler(top_sub_path, LambdaTarget(lambda_splitter))

    return lambda_splitter_top, top_sub_path, sub_path, top_path_parameter_key, return_value, mock_method


@pytest.fixture
def setup_lambda_splitter_with_unsupported_handler():
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    sub_path = 'sub_path'
    # noinspection PyTypeChecker
    lambda_splitter.add_sub_handler(sub_path, "unsupported-handler")

    return lambda_splitter, sub_path


@pytest.fixture
def setup_lambda_splitter_with_json_handler():
    return_value = {RESPONSE_STATUS_CODE_FIELD: 200}
    mock_method = Mock(return_value=return_value)

    def handler_method(json): return mock_method(json=json)
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    sub_path = 'sub_path'
    lambda_splitter.add_sub_handler(sub_path, LambdaTarget(handler_method))
    return lambda_splitter, mock_method, return_value, sub_path


@pytest.fixture
def setup_lambda_splitter_with_method_handler_throws_http_aware_exception(request):
    mock_method = Mock(side_effect=request.param)

    def handler_method(): return mock_method()
    lambda_splitter = LambdaSplitter(PATH_PARAMETER_KEY)
    sub_path = 'sub_path'
    lambda_splitter.add_sub_handler(sub_path, LambdaTarget(handler_method))
    return lambda_splitter, mock_method, sub_path


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


def test_call_when_handler_is_a_method(setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = setup_lambda_splitter_with_method_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path), {})

    mock_method.assert_called_once_with()
    assert result == return_value


def test_call_when_method_not_supported(setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = setup_lambda_splitter_with_method_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path, method='POST'), {})

    mock_method.assert_not_called()
    assert isinstance(result, dict)
    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 405


def test_call_when_no_subpath_match(setup_lambda_splitter_with_method_handler):
    lambda_splitter, mock_method, return_value, sub_path = setup_lambda_splitter_with_method_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, 'unknown_path'), {})

    mock_method.assert_not_called()

    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 404
    assert RESPONSE_BODY_FIELD in result
    assert result[RESPONSE_BODY_FIELD] == "{{\"error\": \"could not find path for this command, " \
                                          "possible paths are [ {} ]\"}}".format(sub_path)


def test_call_embedded_splitter(setup_embedded_lambda_splitter):
    lambda_splitter_top, top_sub_path, sub_path, top_path_parameter_key, return_value, mock_method = \
        setup_embedded_lambda_splitter

    event = {
        'httpMethod': 'GET',
        'pathParameters': {
            top_path_parameter_key: top_sub_path,
            PATH_PARAMETER_KEY: sub_path
        },
        'body': ''
    }

    result = lambda_splitter_top.__call__(event, {})

    mock_method.assert_called_once_with()
    assert result == return_value


def test_runtime_error_when_target_is_not_supported(setup_lambda_splitter_with_unsupported_handler):
    lambda_splitter, sub_path = setup_lambda_splitter_with_unsupported_handler
    with pytest.raises(RuntimeError):
        lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path), {})


def test_json_body(setup_lambda_splitter_with_json_handler):
    lambda_splitter, mock_method, _, sub_path = setup_lambda_splitter_with_json_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path, '{"some-field": "some-value"}'), {})

    mock_method.assert_called_once_with(json={'some-field': 'some-value'})
    assert isinstance(result, dict)
    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 200


def test_json_body_when_not_valid_json(setup_lambda_splitter_with_json_handler):
    lambda_splitter, mock_method, _, sub_path = setup_lambda_splitter_with_json_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path, ''), {})

    mock_method.assert_not_called()
    assert isinstance(result, dict)
    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 400
    assert RESPONSE_BODY_FIELD in result
    assert result[RESPONSE_BODY_FIELD] == '{"error": "body must be a valid JSON"}'


def test_json_body_when_unexpected_exception(setup_lambda_splitter_with_json_handler):
    lambda_splitter, mock_method, _, sub_path = setup_lambda_splitter_with_json_handler

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path, None), {})

    mock_method.assert_not_called()
    assert isinstance(result, dict)
    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 400
    assert RESPONSE_BODY_FIELD in result
    assert result[RESPONSE_BODY_FIELD] == '{"error": "error while trying to handle body", "exception": "the JSON ' \
                                          'object must be str, bytes or bytearray, not NoneType"}'


@pytest.mark.parametrize('setup_lambda_splitter_with_method_handler_throws_http_aware_exception',
                         [HTTPAwareException(status_code=400, error_message='some error!')],
                         ids=['400'],
                         indirect=True)
def test_http_aware_exception(setup_lambda_splitter_with_method_handler_throws_http_aware_exception):
    lambda_splitter, mock_method, sub_path = setup_lambda_splitter_with_method_handler_throws_http_aware_exception

    result = lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, sub_path, None), {})

    mock_method.assert_called_once_with()
    assert isinstance(result, dict)
    assert RESPONSE_STATUS_CODE_FIELD in result
    assert result[RESPONSE_STATUS_CODE_FIELD] == 400
    assert RESPONSE_BODY_FIELD in result
    assert result[RESPONSE_BODY_FIELD] == '{"error": "some error!"}'


@pytest.fixture
def lambda_splitter_with_failing_validation():
    validator_mock = Mock()
    validator_mock.validate.side_effect = RuntimeError("some validation error")
    lambda_target = LambdaTarget(SUCCESS_MOCK, validators=[validator_mock])
    return setup_lambda_splitter(lambda_target)


def test_lambda_splitter_with_failing_validation(lambda_splitter_with_failing_validation):
    lambda_splitter = lambda_splitter_with_failing_validation

    with pytest.raises(RuntimeError):
        lambda_splitter.__call__(_generate_event(PATH_PARAMETER_KEY, DEFAULT_SUB_PATH, None), {})
