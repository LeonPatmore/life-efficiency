from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import Enum
from functools import partial

from dynamo.dynamo_repository import dynamo_item
from helpers.datetime import datetime_to_string
from repository.repository import Repository


@dynamo_item("balance_instances")
@dataclass(frozen=True)
class BalanceInstance:
    holder: str
    amount: float
    date: datetime or None
    id: str = None


class ChangeReason(Enum):
    SALARY = partial(lambda base_amount, change_amount: base_amount - change_amount)
    YEARLY_SPEND = partial(lambda base_amount, change_amount: base_amount + change_amount)
    INVESTMENT = partial(lambda base_amount, change_amount: base_amount + change_amount)

    @staticmethod
    def from_string(name):
        for member in ChangeReason:
            if member.name.lower() == name.lower():
                return member
        raise KeyError(f"{name} is not a valid {ChangeReason.__name__}")


@dynamo_item("balance_changes")
@dataclass(frozen=True)
class BalanceChange:
    reason: ChangeReason
    amount: float
    date: datetime
    id: str = None


class BalanceChangeManager(Repository[BalanceChange]):

    def __init__(self, date_generator: callable):
        super().__init__(BalanceChange)
        self.date_generator = date_generator

    def add(self, item: BalanceChange) -> BalanceChange:
        date = item.date if item.date is not None else self.date_generator()
        return super().add(replace(item, date=date))

    def get_all_between_dates(self, start_date: datetime, end_date: datetime):
        return [x for x in self.get_all() if start_date <= x.date <= end_date]


class BalanceInstanceManager(Repository[BalanceInstance]):

    def __init__(self, date_generator: callable):
        super().__init__(BalanceInstance)
        self.date_generator = date_generator

    def add(self, item: BalanceInstance) -> BalanceInstance:
        date = item.date if item.date is not None else self.date_generator()
        return super().add(replace(item, date=date))


@dataclass(frozen=True)
class BalanceHolderInstantSummary:
    increase: float or None
    holder: str
    amount: float


@dataclass
class BalanceInstantSummary:
    holders: list[BalanceHolderInstantSummary]
    total: float
    total_increase: float or None
    balance_changes: set[BalanceChange]


@dataclass
class BalanceRange:
    balances: dict[datetime, BalanceInstantSummary]
    all_holders: set[str]
    step: timedelta

    def to_json(self):
        return {
            "balances": {datetime_to_string(x): y for x, y in self.balances.items()},
            "all_holders": self.all_holders,
            "step": self.step
        }


class FinanceManager:

    def __init__(self,
                 date_generator: callable,
                 balance_instance_manager: BalanceInstanceManager,
                 balance_change_manager: BalanceChangeManager):
        self.date_generator = date_generator
        self.balance_instance_manager = balance_instance_manager
        self.balance_change_manager = balance_change_manager

    def get_balances_at(self, date: datetime) -> list[BalanceInstance]:
        balances = {}
        for balance in self.balance_instance_manager.get_all():
            if balance.holder in balances:
                balances[balance.holder].append(balance)
            else:
                balances[balance.holder] = [balance]

        final_list = []
        for holder_balances in balances.values():
            in_date_balances = [x for x in holder_balances if x.date <= date]
            sorted_balances = sorted(in_date_balances, key=lambda x: x.date.timestamp(), reverse=True)
            if len(sorted_balances) > 0:
                final_list.append(sorted_balances[0])
        return final_list

    def generate_balance_range(self,
                               start_date: datetime,
                               end_date: datetime or None = None,
                               step: timedelta = timedelta(weeks=1)) -> BalanceRange:
        if end_date is None:
            end_date = self.date_generator()
        all_holders = set()
        balance_map = {}
        current_date = start_date
        previous_date = None
        previous_summary = None
        while current_date <= end_date:
            balances = self.get_balances_at(current_date)
            total = sum([x.amount for x in balances])

            def generate_balance_holder_instant_summary(balance_instance: BalanceInstance) -> (
                    BalanceHolderInstantSummary):
                holder = balance_instance.holder
                amount = balance_instance.amount
                all_holders.add(holder)

                def get_increase():
                    if not previous_summary:
                        return None
                    previous_holders_map = {x.holder: x for x in previous_summary.holders}
                    if holder in previous_holders_map:
                        return amount - previous_holders_map[holder].amount
                    else:
                        return None

                return BalanceHolderInstantSummary(increase=get_increase(), holder=holder, amount=amount)

            total_increase = total - previous_summary.total if previous_summary else None
            holder_summaries = list(map(generate_balance_holder_instant_summary, balances))
            balance_changes = self.balance_change_manager.get_all_between_dates(previous_date, current_date) \
                if previous_date else set()
            instance_summary = BalanceInstantSummary(holder_summaries, total, total_increase, balance_changes)
            balance_map[current_date] = instance_summary
            previous_date = current_date
            previous_summary = instance_summary
            current_date += step
        return BalanceRange(balance_map, all_holders, step=step)

    @staticmethod
    def get_increase_after_normalisation(instant_summary: BalanceInstantSummary) -> float or None:
        final_increase = instant_summary.total_increase
        if final_increase is None:
            return None
        for change in instant_summary.balance_changes:
            # noinspection PyCallingNonCallable
            final_increase = change.reason.value(final_increase, change.amount)
        return final_increase
