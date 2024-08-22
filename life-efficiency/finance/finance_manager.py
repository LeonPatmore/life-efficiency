from dataclasses import dataclass
from datetime import datetime

from dynamo.dynamo_repository import dynamo_item
from repository.repository import Repository


@dynamo_item("balance_instances")
@dataclass
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
