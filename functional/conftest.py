import boto3
import gspread
import pytest

from functional.spreadsheet_helper import SpreadsheetHelper


@pytest.fixture(scope="session")
def load_spreadsheet() -> SpreadsheetHelper:
    file_name = "credentials.json"
    s3_client = boto3.client("s3")
    s3_client.download_file("life-efficiency", "credentials.json", file_name)
    gc = gspread.service_account(filename=file_name)
    spreadsheet = gc.open_by_key("1vuE4S2-tcLKld4VYEMLsKX1MPxVfKr9pZ3kpR1n2eOQ")
    return SpreadsheetHelper(spreadsheet)
