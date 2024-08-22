from dataclasses import dataclass
from datetime import datetime

from dynamo.dynamo_repository import dynamo_item


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


class BalanceInstanceManager:

    def add_instance(self, instance: BalanceInstance) -> BalanceInstance:
        raise NotImplementedError

    def get_instances(self) -> list[BalanceInstance]:
        raise NotImplementedError
