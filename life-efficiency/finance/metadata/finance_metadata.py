from dataclasses import dataclass
from datetime import timedelta

WEEKS_IN_YEAR = 52.1429
DAYS_IN_YEAR = 365.0


@dataclass
class StoredFinanceMetadata:
    monthly_salary: float
    monthly_tax: float


@dataclass
class FinanceMetadata(StoredFinanceMetadata):
    yearly_salary: float
    yearly_tax: float
    weekly_salary: float
    weekly_tax: float

    def __init__(self, stored: StoredFinanceMetadata):
        self.monthly_salary = stored.monthly_salary
        self.monthly_tax = stored.monthly_tax
        self.yearly_salary = stored.monthly_salary * 12.0
        self.yearly_tax = stored.monthly_tax * 12.0
        self.weekly_salary = self.yearly_salary / WEEKS_IN_YEAR
        self.weekly_tax = self.yearly_tax / WEEKS_IN_YEAR
        self.daily_salary = self.yearly_salary / DAYS_IN_YEAR
        self.daily_tax = self.yearly_tax / DAYS_IN_YEAR
        self.daily_take_home = self.daily_salary - self.daily_tax

    def get_take_home_for_timedelta(self, delta: timedelta) -> float:
        return delta.days * self.daily_take_home


class FinanceMetadataLoader:

    def _load_finance_metadata(self) -> StoredFinanceMetadata:
        raise NotImplementedError

    def get_metadata(self) -> FinanceMetadata:
        return FinanceMetadata(self._load_finance_metadata())
