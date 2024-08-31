from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from finance.finance_manager import FinanceManager, BalanceInstance

START_TIME = datetime(year=2024, month=1, day=1)


@pytest.fixture
def setup_finance_manager():
    balance_instance_manager_mock = Mock()
    manager = FinanceManager(balance_instance_manager_mock)
    return manager, balance_instance_manager_mock


def test_get_balances_at(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [BalanceInstance("bank", 100.0, START_TIME)]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 100.0, START_TIME)]


def test_get_balances_at_ignores_instances_after_date(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [BalanceInstance("bank", 100.0, START_TIME)]

    balances = manager.get_balances_at(START_TIME - timedelta(days=1))
    assert balances == []


def test_get_balances_at_takes_latest_value(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME - timedelta(days=5)),
        BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1)),
        BalanceInstance("bank", 300.0, START_TIME - timedelta(days=10)),
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1))]


def test_get_balances_multiple_holders(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME),
        BalanceInstance("investment", 200.0, START_TIME)
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 100.0, START_TIME),
                        BalanceInstance("investment", 200.0, START_TIME)]


def test_generate_balance_range(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME + timedelta(weeks=1)),
        BalanceInstance("investment", 200.0, START_TIME + timedelta(weeks=1)),
        BalanceInstance("bank", 150.0, START_TIME + timedelta(weeks=2)),
        BalanceInstance("investment", 190.0, START_TIME + timedelta(weeks=2)),
    ]

    balance_range = manager.generate_balance_range(START_TIME,
                                                   START_TIME + timedelta(weeks=3),
                                                   timedelta(weeks=1))
    assert len(balance_range.balances) == 4
    assert balance_range.all_holders == {"bank", "investment"}
    assert len(balance_range.balances[START_TIME].holders) == 0
    assert balance_range.balances[START_TIME].total == 0.0
    assert balance_range.balances[START_TIME].total_increase is None
    assert len(balance_range.balances[START_TIME + timedelta(weeks=1)].holders) == 2
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].total == 300.0
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].increase is None
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].amount == 100.0
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].increase is None
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].amount == 200.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=2)].holders) == 2
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].total == 340.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].total_increase == 40.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].increase == 50.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].amount == 150.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].increase == -10.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].amount == 190.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=3)].holders) == 2
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].total == 340.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].total_increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].amount == 150.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].amount == 190.0
