import json

from finance.metadata.finance_metadata import FinanceMetadataLoader, StoredFinanceMetadata


class FinanceMetadataS3Loader(FinanceMetadataLoader):

    def __init__(self, s3_client, bucket: str):
        self.s3_client = s3_client
        self.bucket = bucket

    def _load_finance_metadata(self) -> StoredFinanceMetadata:
        obj = self.s3_client.get_object(Bucket=self.bucket, Key="metadata.json")
        metadata_object = json.loads(obj['Body'].read().decode('utf-8'))
        return StoredFinanceMetadata(metadata_object["monthly_salary"], metadata_object["monthly_tax"])
