from dataclasses import dataclass, replace
from datetime import datetime

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("balance_instances")
@dataclass(frozen=True)
class BalanceInstance:
    holder: str
    amount: float
    date: datetime or None
    id: str = None


class BalanceInstanceManager(Repository[BalanceInstance]):

    def __init__(self, date_generator: callable):
        super().__init__(BalanceInstance)
        self.date_generator = date_generator

    def add(self, item: BalanceInstance) -> BalanceInstance:
        date = item.date if item.date is not None else self.date_generator()
        return super().add(replace(item, date=date))
