from io import BytesIO


class UploaderService:

    def upload(self, file_name: str, file_stream: BytesIO, content_type: str):
        raise NotImplementedError
