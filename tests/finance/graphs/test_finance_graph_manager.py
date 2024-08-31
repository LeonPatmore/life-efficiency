from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from finance.finance_manager import BalanceRange, BalanceInstantSummary
from finance.graphs.finance_graph_manager import FinanceGraphManager


DATE_TIME = datetime(2000, 1, 1, 12, 0, 0)


@pytest.fixture
def setup_finance_graph_manager():
    finance_manager_mock = Mock()
    return FinanceGraphManager(finance_manager_mock), finance_manager_mock


def test_generate_weekly_graph(setup_finance_graph_manager):
    graph_manager, finance_manager = setup_finance_graph_manager

    finance_manager.generate_balances.return_value = BalanceRange({
        DATE_TIME: BalanceInstantSummary(set(), 1000.0),
        DATE_TIME + timedelta(weeks=1): BalanceInstantSummary(set(), 1100.0),
        DATE_TIME + timedelta(weeks=2): BalanceInstantSummary(set(), 900.0),
        DATE_TIME + timedelta(weeks=3): BalanceInstantSummary(set(), 1500.0)
    })

    graph_manager.generate_weekly_graph(DATE_TIME, DATE_TIME + timedelta(weeks=3), step=timedelta(weeks=1))
