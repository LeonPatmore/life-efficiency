import json
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from finance.balance_change_manager import ChangeReason, BalanceChange
from finance.balance_instance_manager import BalanceInstance
from finance.finance_manager import BalanceRange
from finance.finance_manager_handler import FinanceHandler
from helpers.datetime import get_current_datetime_utc, DatetimeCustom
from tests.test_helpers import lambda_http_event


@pytest.fixture
def setup_finance_handler():
    balance_instance_mock = Mock()
    balance_changes_mock = Mock()
    finance_manager_mock = Mock()
    finance_manager_mock.balance_instance_manager = balance_instance_mock
    finance_manager_mock.balance_change_manager = balance_changes_mock
    finance_handler = FinanceHandler(finance_manager_mock)
    return balance_instance_mock, balance_changes_mock, finance_manager_mock, finance_handler


def test_create_balance_instance_with_date(setup_finance_handler):
    balance_instance_mock, _, _, finance_handler = setup_finance_handler
    balance_instance_mock.add.return_value = BalanceInstance("bank", 1000.0, get_current_datetime_utc())

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0, "holder": "bank", "date": "01/01/2000, 00:00:00"}""",
                                            method="POST"))
    assert 200 == res["statusCode"]
    balance_instance_mock.add.assert_called_once_with(BalanceInstance("bank", 1000.0, datetime(2000, 1, 1, 0, 0, 0)))


def test_create_balance_instance_date_is_optional(setup_finance_handler):
    balance_instance_mock, _, _, finance_handler = setup_finance_handler
    balance_instance_mock.add.return_value = BalanceInstance("bank", 1000.0, get_current_datetime_utc())

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0, "holder": "bank"}""",
                                            method="POST"))
    assert 200 == res["statusCode"]
    balance_instance_mock.add.assert_called_once_with(BalanceInstance("bank", 1000.0, None))


def test_create_balance_amount_is_required(setup_finance_handler):
    _, _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"holder": "bank"}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `amount` is required"}


def test_create_balance_holder_is_required(setup_finance_handler):
    _, _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"amount": 1000.0}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `holder` is required"}


def test_create_balance_amount_must_be_float(setup_finance_handler):
    _, _, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance",
                                            "instances",
                                            """{"holder": "bank", "amount": "1000.0"}""",
                                            method="POST"))
    assert 400 == res["statusCode"]
    assert json.loads(res["body"]) == {"error": "field `amount` must be of type float"}


def test_get_changes(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler
    balance_changes_mock.get_all.return_value = [BalanceChange(
        ChangeReason.SALARY, 100.0, datetime(2012, 3, 2, 5, 1, 2), "some desc", "some-id")]

    res = finance_handler(lambda_http_event("finance", "changes"))
    assert 200 == res["statusCode"]
    assert json.loads(res["body"]) == [{
        "amount": 100.0,
        "date": "02/03/2012, 05:01:02",
        "id": "some-id",
        "reason": "salary",
        "desc": "some desc"
    }]


def test_add_change_invalid_reason(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "changes", body=json.dumps({
        "amount": 100.0,
        "desc": "some desc",
        "reason": "asd"
    }), method="POST"))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `reason` is not valid, possible values are ['SALARY', 'YEARLY_SPEND', 'INVESTMENT']"


def test_add_change_missing_reason(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "changes", body=json.dumps({
        "amount": 100.0,
        "desc": "some desc"
    }), method="POST"))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `reason` is required"


def test_add_change_missing_amount(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "changes", body=json.dumps({
        "reason": "salary",
        "desc": "some desc"
    }), method="POST"))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `amount` is required"


def test_add_change_missing_desc(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "changes", body=json.dumps({
        "reason": "salary",
        "amount": 100.0,
    }), method="POST"))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "field `desc` is required"


def test_finance_range_missing_start_date(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "range", query_params={}))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "param `start_date` is required"


def test_finance_range_start_date_invalid_format(setup_finance_handler):
    _, balance_changes_mock, _, finance_handler = setup_finance_handler

    res = finance_handler(lambda_http_event("finance", "range", query_params={
        "start_date": "abc123"
    }))

    assert 400 == res["statusCode"]
    body = json.loads(res["body"])
    assert body["error"] == "time data 'abc123' does not match format '%d/%m/%Y, %H:%M:%S'"


def test_finance_range_start_date_and_end_date(setup_finance_handler):
    _, _, finance_manager_mock, finance_handler = setup_finance_handler
    finance_manager_mock.generate_balance_range.return_value = BalanceRange({}, set(), timedelta(weeks=1))

    res = finance_handler(lambda_http_event("finance", "range", query_params={
        "start_date": "01/01/2000, 12:00:00",
        "end_date": "01/01/2000, 12:00:00"
    }))

    finance_manager_mock.generate_balance_range.assert_called_once_with(
        start_date=DatetimeCustom(2000, 1, 1, 12, 0),
        end_date=DatetimeCustom(2000, 1, 1, 12, 0)
    )

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert body == {
        "all_holders": [],
        "balances": {},
        "step": "7 days, 0:00:00"
    }


def test_finance_range_start_date_without_end_date(setup_finance_handler):
    _, _, finance_manager_mock, finance_handler = setup_finance_handler
    finance_manager_mock.generate_balance_range.return_value = BalanceRange({}, set(), timedelta(weeks=1))

    res = finance_handler(lambda_http_event("finance", "range", query_params={
        "start_date": "01/01/2000, 12:00:00"
    }))

    finance_manager_mock.generate_balance_range.assert_called_once_with(
        start_date=DatetimeCustom(2000, 1, 1, 12, 0),
        end_date=None
    )

    assert 200 == res["statusCode"]
    body = json.loads(res["body"])
    assert body == {
        "all_holders": [],
        "balances": {},
        "step": "7 days, 0:00:00"
    }
