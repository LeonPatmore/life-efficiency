from helpers.lambda_splitter import LambdaSplitter


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
