import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from finance.finance_manager import BalanceInstance, BalanceChange, ChangeReason
from finance.finance_manager_handler import FinanceHandler
from helpers.datetime import get_current_datetime_utc
from tests.test_helpers import lambda_http_event


@pytest.fixture
def setup_finance_handler():
    balance_instance_mock = Mock()
    balance_changes_mock = Mock()
    finance_manager_mock = Mock()
    finance_manager_mock.balance_instance_manager = balance_instance_mock
    finance_manager_mock.balance_change_manager = balance_changes_mock
    finance_handler = FinanceHandler(finance_manager_mock)
    return balance_instance_mock, balance_changes_mock, finance_handler


def test_create_balance_instance_with_date(setup_finance_handler):
    balance_instance_mock, _, finance_handler = setup_finance_handler
    balance_instance_mock.add.return_value = BalanceInstance("bank", 1000.0, get_current_datetime_utc())

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0, "holder": "bank", "date": "01/01/2000, 00:00:00"}""",
                                            method="POST"))
    assert 200 == res["statusCode"]
    balance_instance_mock.add.assert_called_once_with(BalanceInstance("bank", 1000.0, datetime(2000, 1, 1, 0, 0, 0)))


def test_create_balance_instance_date_is_optional(setup_finance_handler):
    balance_instance_mock, _, finance_handler = setup_finance_handler
    balance_instance_mock.add.return_value = BalanceInstance("bank", 1000.0, get_current_datetime_utc())

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0, "holder": "bank"}""",
                                            method="POST"))
    assert 200 == res["statusCode"]
    balance_instance_mock.add.assert_called_once_with(BalanceInstance("bank", 1000.0, None))


def test_create_balance_amount_is_required(setup_finance_handler):
    _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"holder": "bank"}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `amount` is required"}


def test_create_balance_holder_is_required(setup_finance_handler):
    _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `holder` is required"}


def test_create_balance_amount_must_be_float(setup_finance_handler):
    _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"holder": "bank", "amount": "1000.0"}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `amount` must be of type float"}


def test_get_changes(setup_finance_handler):
    _, balance_changes_mock, finance_handler = setup_finance_handler
    balance_changes_mock.get_all.return_value = [BalanceChange(ChangeReason.SALARY, 100.0, datetime(2012, 3, 2, 5, 1, 2))]

    res = finance_handler(lambda_http_event("finance", "changes"))
    assert 200 == res["statusCode"]
    assert json.loads(res["body"]) == [{
        "amount": 100.0,
        "date": "02/03/2012, 05:01:02",
        "reason": "salary"
    }]
