from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from gp2gp.uploader import MeshS3Uploader


def build_mock_file(file_path, date_delivered):
    mock_file = MagicMock()
    mock_file.path = Path(file_path)
    mock_file.read_delivery_date = lambda: date_delivered
    return mock_file


def test_upload():
    mock_s3 = MagicMock()
    bucket_name = "test_bucket"
    file_path = "test/file.dat"

    uploader = MeshS3Uploader(mock_s3, bucket_name)

    a_file = build_mock_file(file_path, datetime(2020, 3, 4))
    uploader.upload(a_file)

    mock_s3.upload_file.assert_called_once_with(file_path, bucket_name, "2020/03/04/file.dat")
