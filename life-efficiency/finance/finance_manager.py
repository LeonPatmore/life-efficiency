from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import groupby

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("balance_instances")
@dataclass(frozen=True)
class BalanceInstance:
    holder: str
    amount: float
    date: datetime
    id: str = None


class ChangeReason(enumerate):
    SALARY = 0
    YEARLY_SPEND = 1
    INVESTMENT = 2


@dataclass
class BalanceChange:
    reason: ChangeReason
    amount: float
    date: datetime


class BalanceInstanceManager(Repository[BalanceInstance]):

    def __init__(self):
        super().__init__(BalanceInstance)


@dataclass
class BalanceInstantSummary:
    holders: set[BalanceInstance]
    total: float


@dataclass
class BalanceRange:
    balances: dict[datetime, BalanceInstantSummary]


class FinanceManager:

    def __init__(self, balance_instance_manager: BalanceInstanceManager):
        self.balance_instance_manager = balance_instance_manager

    def get_balances_at(self, date: datetime) -> set[BalanceInstance]:
        balances = {k: list(v) for k, v in groupby(self.balance_instance_manager.get_all(), lambda x: x.holder)}
        final_set = set()
        for holder_balances in balances.values():
            in_date_balances = [x for x in holder_balances if x.date <= date]
            sorted_balances = sorted(in_date_balances, key=lambda x: x.date.timestamp(), reverse=True)
            if len(sorted_balances) > 0:
                final_set.add(sorted_balances[0])
        return final_set

    def generate_balances(self, start_date: datetime, end_date: datetime, step: timedelta) -> BalanceRange:
        balance_range = BalanceRange({})
        current_date = start_date
        while current_date < end_date:
            balances = self.get_balances_at(current_date)
            total = sum([x.amount for x in balances])
            balance_range.balances[current_date] = BalanceInstantSummary(balances, total)
            current_date += step
        return balance_range
