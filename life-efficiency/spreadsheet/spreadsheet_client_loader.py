import os

import gspread

SPREADSHEET_KEY_ENV_VAR = "SPREADSHEET_KEY"

SPREADSHEET_AWS_S3_BUCKET_NAME_ENV_VAR = "SPREADSHEET_AWS_S3_BUCKET_NAME"
SPREADSHEET_AWS_S3_FILE_NAME_ENV_VAR = "SPREADSHEET_AWS_S3_FILE_NAME"


class SpreadsheetLoader(object):

    def __init__(self):
        gc = gspread.service_account(filename=self._get_credentials_filename())
        self.spreadsheet = gc.open_by_key(self._get_spreadsheet_key())

    @staticmethod
    def _get_spreadsheet_key():
        key = os.environ.get(SPREADSHEET_KEY_ENV_VAR, None)
        if not key:
            raise RuntimeError("No spreadsheet key environment variable discovered!")
        return key

    def _get_credentials_filename(self):
        raise NotImplementedError()


class SpreadsheetLoaderAWS(SpreadsheetLoader):

    def __init__(self, s3_client):
        self.s3_client = s3_client
        self.bucket_name = os.environ.get(SPREADSHEET_AWS_S3_BUCKET_NAME_ENV_VAR, "life-efficiency")
        self.s3_file_name = os.environ.get(SPREADSHEET_AWS_S3_FILE_NAME_ENV_VAR, "credentials.json")
        super().__init__()

    def _get_credentials_filename(self):
        file_name = "/tmp/credentials.json"
        self.s3_client.download_file(self.bucket_name, self.s3_file_name, file_name)
        return file_name
