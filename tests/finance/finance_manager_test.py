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


def test_generate_balances(setup_finance_manager):
    manager, balance_instance_manager_mock = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME + timedelta(weeks=1)),
        BalanceInstance("investment", 200.0, START_TIME + timedelta(weeks=1)),
        BalanceInstance("bank", 150.0, START_TIME + timedelta(weeks=2)),
        BalanceInstance("investment", 190.0, START_TIME + timedelta(weeks=2)),
    ]

    balances = manager.generate_balances(START_TIME,
                                         START_TIME + timedelta(weeks=3),
                                         timedelta(weeks=1))
    assert len(balances.balances) == 4
    assert len(balances.balances[START_TIME].holders) == 0
    assert balances.balances[START_TIME].total == 0.0
    assert len(balances.balances[START_TIME + timedelta(weeks=1)].holders) == 2
    assert balances.balances[START_TIME + timedelta(weeks=1)].total == 300.0
    assert len(balances.balances[START_TIME + timedelta(weeks=2)].holders) == 2
    assert balances.balances[START_TIME + timedelta(weeks=2)].total == 340.0
    assert len(balances.balances[START_TIME + timedelta(weeks=3)].holders) == 2
    assert balances.balances[START_TIME + timedelta(weeks=3)].total == 340.0
