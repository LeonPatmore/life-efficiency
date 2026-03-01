from dataclasses import replace, dataclass
from datetime import datetime
from enum import Enum

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


class ChangeReason(Enum):
    SALARY = "salary"
    YEARLY_SPEND = "yearly_spend"
    INVESTMENT = "investment"

    @staticmethod
    def from_string(name):
        for member in ChangeReason:
            if member.name.lower() == name.lower():
                return member
        raise KeyError(f"{name} is not a valid {ChangeReason.__name__}")

    def apply(self, base_amount: float, change_amount: float) -> float:
        if self == ChangeReason.SALARY:
            return base_amount - change_amount
        return base_amount + change_amount


@dynamo_item("balance_changes")
@dataclass(frozen=True)
class BalanceChange:
    reason: ChangeReason
    amount: float
    date: datetime
    desc: str
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
