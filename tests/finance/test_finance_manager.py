from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from finance.balance_change_manager import BalanceChange, ChangeReason
from finance.balance_instance_manager import BalanceInstance
from finance.finance_manager import FinanceManager

START_TIME = datetime(year=2024, month=1, day=1)


@pytest.fixture
def setup_finance_manager():
    balance_instance_manager_mock = Mock()
    balance_change_manager_mock = Mock()
    metadata_loader_mock = Mock()
    manager = FinanceManager(lambda: datetime(year=2000, month=1, day=1),
                             balance_instance_manager_mock,
                             balance_change_manager_mock,
                             metadata_loader_mock)
    return manager, balance_instance_manager_mock, balance_change_manager_mock


def test_get_balances_at(setup_finance_manager):
    manager, balance_instance_manager_mock, _ = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [BalanceInstance("bank", 100.0, START_TIME)]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 100.0, START_TIME)]


def test_get_balances_at_ignores_instances_after_date(setup_finance_manager):
    manager, balance_instance_manager_mock, _ = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [BalanceInstance("bank", 100.0, START_TIME)]

    balances = manager.get_balances_at(START_TIME - timedelta(days=1))
    assert balances == []


def test_get_balances_at_takes_latest_value(setup_finance_manager):
    manager, balance_instance_manager_mock, _ = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME - timedelta(days=5)),
        BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1)),
        BalanceInstance("bank", 300.0, START_TIME - timedelta(days=10)),
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 200.0, START_TIME - timedelta(days=1))]


def test_get_balances_multiple_holders(setup_finance_manager):
    manager, balance_instance_manager_mock, _ = setup_finance_manager

    balance_instance_manager_mock.get_all.return_value = [
        BalanceInstance("bank", 100.0, START_TIME),
        BalanceInstance("investment", 200.0, START_TIME)
    ]

    balances = manager.get_balances_at(START_TIME + timedelta(days=1))
    assert balances == [BalanceInstance("bank", 100.0, START_TIME),
                        BalanceInstance("investment", 200.0, START_TIME)]


def test_generate_balance_range(setup_finance_manager):
    manager, balance_instance_manager_mock, balance_change_manager_mock = setup_finance_manager

    balance_change_manager_mock.get_all_between_dates.side_effect = [
        [BalanceChange(ChangeReason.SALARY, 100.0, START_TIME + timedelta(days=4), "salary")],
        [],
        []
    ]
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
    assert len(balance_range.balances[START_TIME + timedelta(weeks=1)].balance_changes) == 1
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].total_increase == 300.0
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].total_increase_normalised == 200.0
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].increase is None
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[0].amount == 100.0
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].increase is None
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=1)].holders[1].amount == 200.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=2)].holders) == 2
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].total == 340.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=2)].balance_changes) == 0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].total_increase == 40.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].total_increase_normalised == 40.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].increase == 50.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[0].amount == 150.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].increase == -10.0
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=2)].holders[1].amount == 190.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=3)].holders) == 2
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].total == 340.0
    assert len(balance_range.balances[START_TIME + timedelta(weeks=3)].balance_changes) == 0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].total_increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].total_increase_normalised == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].holder == "bank"
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[0].amount == 150.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].increase == 0.0
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].holder == "investment"
    assert balance_range.balances[START_TIME + timedelta(weeks=3)].holders[1].amount == 190.0
