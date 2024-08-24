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
    assert balances == {BalanceInstance("bank", 100.0, START_TIME)}


def test_get_balances_at_ignores_instances_after_date(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [BalanceInstance("bank", 100.0, START_TIME)]

    balances = manager.get_balances_at(START_TIME - timedelta(days=1))
    assert balances == set()


def test_get_balances_at_takes_latest_value(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME - timedelta(days=5)),
        BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1)),
        BalanceInstance("bank", 300.0, START_TIME - timedelta(days=10)),
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == {BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1))}


def test_get_balances_multiple_holders(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME),
        BalanceInstance("investment", 200.0, START_TIME)
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == {BalanceInstance("bank", 100.0, START_TIME),
                        BalanceInstance("investment", 200.0, START_TIME)}
