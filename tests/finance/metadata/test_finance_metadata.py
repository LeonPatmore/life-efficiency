from datetime import timedelta

from finance.metadata.finance_metadata import FinanceMetadata, StoredFinanceMetadata


def test_finance_metadata():
    metadata = FinanceMetadata(StoredFinanceMetadata(monthly_salary=1000.0, monthly_tax=100.0))

    assert metadata.yearly_salary == 12000.0
    assert metadata.yearly_tax == 1200.0
    assert metadata.monthly_salary == 1000.0
    assert metadata.monthly_tax == 100.0
    assert metadata.weekly_salary == 230.13679714783797
    assert metadata.weekly_tax == 23.013679714783798
    assert metadata.daily_salary == 32.87671232876713
    assert metadata.daily_tax == 3.287671232876712
    assert metadata.daily_take_home == 29.589041095890416


def test_finance_metadata_get_take_home_for_timedelta():
    metadata = FinanceMetadata(StoredFinanceMetadata(monthly_salary=1000.0, monthly_tax=100.0))

    assert metadata.get_take_home_for_timedelta(delta=timedelta(days=1)) == 29.589041095890416
    assert metadata.get_take_home_for_timedelta(delta=timedelta(weeks=1)) == 207.1232876712329
