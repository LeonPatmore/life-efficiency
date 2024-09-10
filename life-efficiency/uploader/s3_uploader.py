from io import BytesIO

from uploader.uploader import UploaderService


class S3Uploader(UploaderService):

    def __init__(self, s3_client, bucket: str):
        self.s3_client = s3_client
        self.bucket = bucket

    def upload(self, file_name: str, file_stream: BytesIO, content_type: str):
        self.s3_client.upload_fileobj(file_stream, self.bucket, file_name, ExtraArgs={
            'ContentType': content_type
        })
        return self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': file_name
            }
        ).replace("localstack", "localhost")
