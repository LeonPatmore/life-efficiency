from datetime import datetime, timedelta

import pytest

from finance.finance_manager import BalanceRange, BalanceInstantSummary, BalanceChange, ChangeReason
from finance.graphs.finance_graph_manager import FinanceGraphManager

DATE_TIME = datetime(2000, 1, 1, 12, 0, 0)


@pytest.fixture
def setup_finance_graph_manager():
    balance_range = BalanceRange({
        DATE_TIME: BalanceInstantSummary([], 1000.0, None, set()),
        DATE_TIME + timedelta(weeks=1): BalanceInstantSummary([], 1100.0, 100.0, set()),
        DATE_TIME + timedelta(weeks=2): BalanceInstantSummary([], 900.0, -100.0, set()),
        DATE_TIME + timedelta(weeks=3):
            BalanceInstantSummary([], 1500.0, 600.0,
                                  {BalanceChange(ChangeReason.SALARY, 700.0, DATE_TIME + timedelta(weeks=2, days=3))}),
        DATE_TIME + timedelta(weeks=4):
            BalanceInstantSummary([], 500.0, -1000.0,
                                  {BalanceChange(ChangeReason.YEARLY_SPEND, 700.0,
                                                 DATE_TIME + timedelta(weeks=3, days=3))})
    }, {"bank", "investment"})
    return FinanceGraphManager(balance_range)


def test_generate_balance_summary(setup_finance_graph_manager):
    graph_manager = setup_finance_graph_manager

    graph_manager.generate_balance_summary().savefig("test-balance-summary")


def test_generate_weekly_difference_summary(setup_finance_graph_manager):
    graph_manager = setup_finance_graph_manager

    graph_manager.generate_weekly_difference_summary().savefig("test-weekly-difference")