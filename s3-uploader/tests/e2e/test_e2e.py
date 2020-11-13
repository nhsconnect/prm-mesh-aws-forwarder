import random
import sqlite3
import string
from datetime import datetime
from os import getenv
from pathlib import Path
from subprocess import Popen, PIPE

import boto3
from botocore.config import Config
from gp2gp.mesh.file import MeshFile
from gp2gp.registry import ProcessedFileRegistry


def _a_string(length=10, characters=string.ascii_letters + string.digits):
    return "".join(random.choice(characters) for _ in range(length))


MINIO_ADDRESS = "localhost:9001"
MINIO_ACCESS_KEY = _a_string()
MINIO_SECRET_KEY = _a_string()
MINIO_REGION = "eu-west-2"


def _start_minio(data_dir):
    minio_command = f"\
            minio server {data_dir} \
            --address {MINIO_ADDRESS} \
            --compat \
        "
    minio_env = {
        "MINIO_ACCESS_KEY": MINIO_ACCESS_KEY,
        "MINIO_SECRET_KEY": MINIO_SECRET_KEY,
        "MINIO_REGION_NAME": MINIO_REGION,
        "HOME": data_dir,
    }

    return Popen(minio_command, env=minio_env, shell=True, stdout=PIPE, stderr=PIPE)


def _write_test_files(test_files):
    for (mesh_file, delivery_date) in test_files:
        ctl_path = mesh_file.path.parent / f"{mesh_file.path.stem}.ctl"
        mesh_file.path.write_text("some-data")
        timestamp = delivery_date.strftime("%Y%m%d%H%M%S")
        ctl_path.write_text(
            (
                "<DTSControl>"
                "<StatusRecord>"
                "<DateTime>"
                f"{timestamp}"
                "</DateTime>"
                "<Event>TRANSFER</Event>"
                "<Status>SUCCESS</Status>"
                "</StatusRecord>"
                "</DTSControl>"
            )
        )


def _write_prior_sqlite_state(state_file, already_processed):
    sqlite_conn = sqlite3.connect(state_file)
    file_registry = ProcessedFileRegistry(sqlite_conn)
    for mesh_file in already_processed:
        file_registry.mark_processed(mesh_file)


def _build_s3_bucket(bucket_name):
    s3 = boto3.resource(
        "s3",
        endpoint_url=f"http://{MINIO_ADDRESS}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name=MINIO_REGION,
    )
    return s3.Bucket(bucket_name)


def _run_synchronizer(mesh_inbox, bucket_name, state_file):
    pipeline_env = {
        "AWS_ACCESS_KEY_ID": MINIO_ACCESS_KEY,
        "AWS_SECRET_ACCESS_KEY": MINIO_SECRET_KEY,
        "AWS_DEFAULT_REGION": MINIO_REGION,
        "PATH": getenv("PATH"),
    }
    pipeline_command = f"\
        sync-mesh-to-s3 \
        --mesh-inbox {str(mesh_inbox)}\
        --s3-bucket {bucket_name} \
        --state-file {str(state_file)} \
        --s3-endpoint-url http://{MINIO_ADDRESS} \
    "
    return Popen(pipeline_command, shell=True, env=pipeline_env, stdout=PIPE, stderr=PIPE)


def test_mesh_s3_synchronizer(tmpdir):
    tmpdir_path = Path(tmpdir)
    minio_data_dir = tmpdir_path / "minio"
    minio_process = _start_minio(minio_data_dir)
    mesh_inbox = tmpdir_path / "IN"
    mesh_inbox.mkdir()
    state_file = tmpdir_path / "state.db"
    bucket_name = "a-bucket"
    s3_bucket = _build_s3_bucket(bucket_name)
    s3_bucket.create()

    mesh_file_one = MeshFile(mesh_inbox / "file_one.dat")
    mesh_file_two = MeshFile(mesh_inbox / "file_two.dat")
    mesh_file_three = MeshFile(mesh_inbox / "file_three.dat")
    mesh_file_four = MeshFile(mesh_inbox / "file_four.dat")

    _write_test_files(
        test_files=[
            (mesh_file_one, datetime(2020, 2, 3, 10, 6, 2)),
            (mesh_file_two, datetime(2020, 2, 3, 11, 52, 18)),
            (mesh_file_three, datetime(2020, 2, 4, 7, 20, 9)),
        ]
    )

    _write_prior_sqlite_state(state_file, already_processed=[mesh_file_one])

    try:
        pipeline_process = _run_synchronizer(mesh_inbox, bucket_name, state_file)
        pipeline_process.wait(timeout=10)
        expected_object_keys_a = {"2020/02/03/file_two.dat", "2020/02/04/file_three.dat"}
        actual_object_keys_a = {obj.key for obj in s3_bucket.objects.all()}
        assert actual_object_keys_a == expected_object_keys_a

        _write_test_files([(mesh_file_four, datetime(2020, 4, 5, 2, 23, 56))])
        pipeline_process = _run_synchronizer(mesh_inbox, bucket_name, state_file)
        pipeline_process.wait(timeout=10)
        expected_object_keys_b = {
            "2020/02/03/file_two.dat",
            "2020/02/04/file_three.dat",
            "2020/04/05/file_four.dat",
        }
        actual_object_keys_b = {obj.key for obj in s3_bucket.objects.all()}
        assert actual_object_keys_b == expected_object_keys_b

    finally:
        minio_process.terminate()
        minio_process.wait()
