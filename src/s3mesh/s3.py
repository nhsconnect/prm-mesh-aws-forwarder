from s3mesh.mesh import MeshMessage


class S3Uploader:
    def __init__(self, s3_client, bucket_name: str):
        self._s3_client = s3_client
        self._bucket_name = bucket_name

    def upload(self, message: MeshMessage):
        key = f"{message.date_delivered.strftime('%Y/%m/%d')}/{message.file_name}"
        self._s3_client.upload_fileobj(message, self._bucket_name, key)