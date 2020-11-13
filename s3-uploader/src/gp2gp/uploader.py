class MeshS3Uploader:
    def __init__(self, s3, bucket_name):
        self._s3 = s3
        self._bucket_name = bucket_name

    def upload(self, mesh_file):
        date_delivered = mesh_file.read_delivery_date()
        key = f"{date_delivered.strftime('%Y/%m/%d')}/{mesh_file.path.name}"
        self._s3.upload_file(str(mesh_file.path), self._bucket_name, key)
