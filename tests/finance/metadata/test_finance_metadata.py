from finance.metadata.finance_metadata import FinanceMetadata, StoredFinanceMetadata


def test_finance_metadata():
    metadata = FinanceMetadata(StoredFinanceMetadata(monthly_salary=1000.0, monthly_tax=100.0))

    assert metadata.yearly_salary == 12000.0
    assert metadata.yearly_tax == 1200.0
    assert metadata.monthly_salary == 1000.0
    assert metadata.monthly_tax == 100.0
    assert metadata.weekly_salary == 230.13679714783797
    assert metadata.weekly_tax == 23.013679714783798
