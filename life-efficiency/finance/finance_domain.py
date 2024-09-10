from dataclasses import dataclass
from datetime import datetime, timedelta

from finance.balance_change_manager import BalanceChange
from helpers.datetime import datetime_to_string


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
    total_increase_normalised: float or None


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
