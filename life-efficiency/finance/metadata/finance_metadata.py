from dataclasses import dataclass

WEEKS_IN_YEAR = 52.1429


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


class FinanceMetadataLoader:

    def _load_finance_metadata(self) -> StoredFinanceMetadata:
        raise NotImplementedError

    def get_metadata(self) -> FinanceMetadata:
        return FinanceMetadata(self._load_finance_metadata())
