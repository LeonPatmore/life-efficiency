import boto3

from spreadsheet.spreadsheet_client_loader import SpreadsheetLoaderAWS

# Only load env in dev.
try:
    import dotenv
except ImportError:
    dotenv = None
if dotenv:
    dotenv.load_dotenv()

spreadsheet = SpreadsheetLoaderAWS(boto3.client("s3")).spreadsheet
