from datetime import datetime, timedelta

from finance.balance_change_manager import BalanceChange, BalanceChangeManager
from finance.balance_instance_manager import BalanceInstanceManager, BalanceInstance
from finance.finance_domain import BalanceHolderInstantSummary, BalanceInstantSummary, BalanceRange
from finance.graphs.finance_graph_manager import FinanceGraphManager
from finance.metadata.finance_metadata import FinanceMetadataLoader


class FinanceManager:

    def __init__(self,
                 date_generator: callable,
                 balance_instance_manager: BalanceInstanceManager,
                 balance_change_manager: BalanceChangeManager,
                 metadata_loader: FinanceMetadataLoader):
        self.date_generator = date_generator
        self.balance_instance_manager = balance_instance_manager
        self.balance_change_manager = balance_change_manager
        self.metadata_loader = metadata_loader

    def get_balances_by_holder(self) -> dict:
        balances = {}
        for balance in self.balance_instance_manager.get_all():
            if balance.holder in balances:
                balances[balance.holder].append(balance)
            else:
                balances[balance.holder] = [balance]
        return balances

    def get_balances_at(self, date: datetime) -> list[BalanceInstance]:
        balances_by_holder = self.get_balances_by_holder()
        final_list = []
        for holder_balances in balances_by_holder.values():
            in_date_balances = [x for x in holder_balances if x.date <= date]
            sorted_balances = sorted(in_date_balances, key=lambda x: x.date.timestamp(), reverse=True)
            if len(sorted_balances) > 0:
                final_list.append(sorted_balances[0])
        return final_list

    def _generate_balance_instant_summary(self,
                                          date: datetime,
                                          previous_date: datetime or None,
                                          previous_summary: BalanceInstantSummary or None) -> BalanceInstantSummary:
        balances = self.get_balances_at(date)
        total = sum([x.amount for x in balances])

        def generate_balance_holder_instant_summary(balance_instance: BalanceInstance) -> (
                BalanceHolderInstantSummary):
            holder = balance_instance.holder
            amount = balance_instance.amount

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
        balance_changes = self.balance_change_manager.get_all_between_dates(previous_date, date) \
            if previous_date else set()
        normalised_increase = self.get_value_after_normalisation(total_increase, balance_changes)
        return BalanceInstantSummary(holder_summaries, total, total_increase, balance_changes, normalised_increase)

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
            instance_summary = self._generate_balance_instant_summary(current_date, previous_date, previous_summary)
            for holder_balance in instance_summary.holders:
                all_holders.add(holder_balance.holder)
            balance_map[current_date] = instance_summary
            previous_date = current_date
            previous_summary = instance_summary
            current_date += step
        return BalanceRange(balance_map, all_holders, step=step)

    @staticmethod
    def get_value_after_normalisation(value: float, changes: list[BalanceChange]) -> float or None:
        for change in changes:
            # noinspection PyCallingNonCallable
            value = change.reason.value(value, change.amount)
        return value

    def generate_graph_manager(self, balance_range: BalanceRange):
        return FinanceGraphManager(balance_range, self.metadata_loader.get_metadata())
