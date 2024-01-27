import json
import os
import uuid
from unittest import mock

import pytest

from tests.test_helpers import cleanup_modules


@pytest.fixture(autouse=True)
def reset_configuration():
    cleanup_modules(["configuration"])
    yield
    cleanup_modules(["configuration"])


@mock.patch.dict(os.environ, {"BACKEND": "dynamo",
                              "AWS_DEFAULT_REGION": "eu-west-1",
                              "AWS_ENDPOINT_URL": "http://localhost:8000"})
def test_shopping_list_adding_items_together():
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})
    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        },
        "body": f"""{{"name": "{item_name}","quantity": 3}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "list"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    item_part = [x for x in body["items"] if x["name"] == item_name][0]
    assert item_part["name"] == item_name
    assert item_part["quantity"] == 6


@mock.patch.dict(os.environ, {"BACKEND": "dynamo",
                              "AWS_DEFAULT_REGION": "eu-west-1",
                              "AWS_ENDPOINT_URL": "http://localhost:8000"})
def test_shopping_list_adding_items_together():
    import configuration

    item_name = str(uuid.uuid4())

    configuration.handler({
        'httpMethod': "POST",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        },
        "body": f"""{{"item": "{item_name}"}}"""
    }, {})

    res = configuration.handler({
        'httpMethod': "GET",
        'pathParameters': {
            "command": "shopping",
            "subcommand": "repeating"
        }
    }, {})

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    item_part = [x for x in body["items"] if x["name"] == item_name][0]
    assert item_part["name"] == item_name
    assert item_part["quantity"] == 6
