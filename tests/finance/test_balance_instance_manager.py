from datetime import datetime

import pytest

from finance.balance_instance_manager import BalanceInstanceManager, BalanceInstance


DATE_TIME_2000 = datetime(year=2000, month=1, day=1)
DATE_TIME_3000 = datetime(year=3000, month=1, day=1)


@pytest.fixture
def setup_balance_instance_manager():
    manager = BalanceInstanceManager(lambda: None)
    manager.get_all = lambda: [
        BalanceInstance("holder-1", 10.0, DATE_TIME_2000),
        BalanceInstance("holder-1", 10.0, DATE_TIME_3000),
        BalanceInstance("holder-2", 10.0, DATE_TIME_2000),
        BalanceInstance("holder-2", 10.0, DATE_TIME_3000),
    ]
    return manager


def test_get_all_with_filters_no_filters(setup_balance_instance_manager):
    manager = setup_balance_instance_manager

    items = manager.get_all_with_filters(None, None)

    assert items == [
        BalanceInstance("holder-1", 10.0, DATE_TIME_2000),
        BalanceInstance("holder-1", 10.0, DATE_TIME_3000),
        BalanceInstance("holder-2", 10.0, DATE_TIME_2000),
        BalanceInstance("holder-2", 10.0, DATE_TIME_3000)
    ]


def test_get_all_with_filters_date_filter(setup_balance_instance_manager):
    manager = setup_balance_instance_manager

    items = manager.get_all_with_filters(None, DATE_TIME_3000)

    assert items == [
        BalanceInstance("holder-1", 10.0, DATE_TIME_3000),
        BalanceInstance("holder-2", 10.0, DATE_TIME_3000)
    ]


def test_get_all_with_filters_holder_filter(setup_balance_instance_manager):
    manager = setup_balance_instance_manager

    items = manager.get_all_with_filters("holder-1", None)

    assert items == [
        BalanceInstance("holder-1", 10.0, DATE_TIME_2000),
        BalanceInstance("holder-1", 10.0, DATE_TIME_3000)
    ]
