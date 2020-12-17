from datetime import datetime
from unittest.mock import MagicMock

from s3mesh.s3 import S3Uploader


def test_upload():
    mock_s3_client = MagicMock()
    bucket_name = "test_bucket"
    mesh_message = MagicMock()
    file_name = "a_file_A1BH13.dat"
    mesh_message.file_name = file_name
    mesh_message.date_delivered = datetime(year=2020, month=11, day=2)

    uploader = S3Uploader(mock_s3_client, bucket_name)
    uploader.upload(mesh_message, MagicMock())

    mock_s3_client.upload_fileobj.assert_called_once_with(
        mesh_message, bucket_name, f"2020/11/02/{file_name}"
    )


def test_upload_records_key():
    mock_s3_client = MagicMock()
    bucket_name = "test_bucket"
    mesh_message = MagicMock()
    file_name = "a_file_A1BH13.dat"
    mesh_message.file_name = file_name
    mesh_message.date_delivered = datetime(year=2020, month=11, day=2)
    observation = MagicMock()

    uploader = S3Uploader(mock_s3_client, bucket_name)

    uploader.upload(mesh_message, observation)
    expected_key = f"2020/11/02/{file_name}"

    observation.add_field.assert_called_once_with("s3Key", expected_key)
