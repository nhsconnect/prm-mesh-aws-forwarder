import re
import ssl
from datetime import datetime
from os import environ, mkdir, path
from threading import Thread
from time import sleep

import boto3
import mesh_client
from cheroot.ssl.builtin import BuiltinSSLAdapter
from cheroot.wsgi import Server
from fake_mesh import FakeMeshApplication
from moto.server import DomainDispatcherApplication, create_backend_app

from s3mesh.entrypoint import build_forwarder_from_environment_variables
from tests.builders.common import a_string


def _bundled_file_path(filename):
    return path.join(path.dirname(mesh_client.__file__), filename)


def _read_file(filepath):
    with open(filepath) as f:
        return f.read()


def _utf_8(string):
    return bytes(string, "utf-8")


CA_CERT_PATH = _bundled_file_path("ca.cert.pem")
SERVER_CERT_PATH = _bundled_file_path("server.cert.pem")
SERVER_KEY_PATH = _bundled_file_path("server.key.pem")
CLIENT_CERT_PATH = _bundled_file_path("client.cert.pem")
CLIENT_KEY_PATH = _bundled_file_path("client.key.pem")

MESH_MAILBOX_SSM_PARAM = "mesh/mailbox-name"
MESH_PASSWORD_SSM_PARAM = "mesh/mailbox-password"
MESH_SHARED_KEY_SSM_PARAM = "mesh/shared-key"
MESH_CLIENT_CERT_SSM_PARAM = "mesh/client-cert"
MESH_CLIENT_KEY_SSM_PARAM = "mesh/client-key"
MESH_CA_CERT_SSM_PARAM = "mesh/ca-cert"

FAKE_MESH_HOST = "127.0.0.1"
FAKE_MESH_PORT = 8829
FAKE_MESH_URL = f"https://localhost:{FAKE_MESH_PORT}"
FAKE_MESH_SHARED_KEY = a_string()
FAKE_MESH_CLIENT_PASSWORD = a_string()

FAKE_AWS_HOST = "127.0.0.1"
FAKE_AWS_PORT = 8887
FAKE_AWS_URL = f"http://{FAKE_AWS_HOST}:{FAKE_AWS_PORT}"

SENDING_MESH_MAILBOX = "e2e-test-mailbox-sender"
RECEIVING_MESH_MAILBOX = "e2e-test-mailbox-receiver"
S3_BUCKET = "e2e-test-bucket"

WAIT_60_SEC = {"Delay": 5, "MaxAttempts": 12}


class ThreadedHttpd:
    def __init__(self, httpd):
        self._httpd = httpd
        self._thread = Thread(target=httpd.safe_start)

    def start(self):
        self._thread.start()

    def stop(self):
        self._httpd.stop()
        self._thread.join()


class ThreadedForwarder:
    def __init__(self, forwarder):
        self._forwarder = forwarder
        self._thread = Thread(target=forwarder.start)

    def start(self):
        self._thread.start()

    def stop(self):
        self._forwarder.stop()
        self._thread.join()


def _build_fake_mesh(mesh_dir):
    app = FakeMeshApplication(mesh_dir, _utf_8(FAKE_MESH_SHARED_KEY), FAKE_MESH_CLIENT_PASSWORD)
    httpd = Server((FAKE_MESH_HOST, FAKE_MESH_PORT), app)

    server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=CA_CERT_PATH)
    server_context.load_cert_chain(SERVER_CERT_PATH, SERVER_KEY_PATH)
    server_context.check_hostname = False
    server_context.verify_mode = ssl.CERT_REQUIRED

    ssl_adapter = BuiltinSSLAdapter(SERVER_CERT_PATH, SERVER_KEY_PATH, CA_CERT_PATH)
    ssl_adapter.context = server_context
    httpd.ssl_adapter = ssl_adapter
    return ThreadedHttpd(httpd)


def _build_fake_aws():
    app = DomainDispatcherApplication(create_backend_app)
    httpd = Server((FAKE_AWS_HOST, FAKE_AWS_PORT), app)
    return ThreadedHttpd(httpd)


def _build_forwarder(forwarder_home):
    env_config = {
        "MESH_URL": FAKE_MESH_URL,
        "MESH_MAILBOX_SSM_PARAM_NAME": MESH_MAILBOX_SSM_PARAM,
        "MESH_PASSWORD_SSM_PARAM_NAME": MESH_PASSWORD_SSM_PARAM,
        "MESH_SHARED_KEY_SSM_PARAM_NAME": MESH_SHARED_KEY_SSM_PARAM,
        "MESH_CLIENT_CERT_SSM_PARAM_NAME": MESH_CLIENT_CERT_SSM_PARAM,
        "MESH_CLIENT_KEY_SSM_PARAM_NAME": MESH_CLIENT_KEY_SSM_PARAM,
        "MESH_CA_CERT_SSM_PARAM_NAME": MESH_CA_CERT_SSM_PARAM,
        "S3_BUCKET_NAME": S3_BUCKET,
        "POLL_FREQUENCY": "5",
        "FORWARDER_HOME": forwarder_home,
        "S3_ENDPOINT_URL": FAKE_AWS_URL,
        "SSM_ENDPOINT_URL": FAKE_AWS_URL,
    }

    forwarder = build_forwarder_from_environment_variables(env_config)
    return ThreadedForwarder(forwarder)


def _build_mesh_client():
    return mesh_client.MeshClient(
        FAKE_MESH_URL,
        SENDING_MESH_MAILBOX,
        FAKE_MESH_CLIENT_PASSWORD,
        shared_key=_utf_8(FAKE_MESH_SHARED_KEY),
        cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
        verify=CA_CERT_PATH,
    )


def _build_s3_resource():
    return boto3.resource(
        service_name="s3",
        endpoint_url=FAKE_AWS_URL,
    )


def _build_ssm_client():
    return boto3.client(
        service_name="ssm",
        endpoint_url=FAKE_AWS_URL,
    )


def _populate_ssm_params(ssm):
    parameters = {
        MESH_MAILBOX_SSM_PARAM: RECEIVING_MESH_MAILBOX,
        MESH_PASSWORD_SSM_PARAM: FAKE_MESH_CLIENT_PASSWORD,
        MESH_SHARED_KEY_SSM_PARAM: FAKE_MESH_SHARED_KEY,
        MESH_CLIENT_CERT_SSM_PARAM: _read_file(CLIENT_CERT_PATH),
        MESH_CLIENT_KEY_SSM_PARAM: _read_file(CLIENT_KEY_PATH),
        MESH_CA_CERT_SSM_PARAM: _read_file(CA_CERT_PATH),
    }
    for name, value in parameters.items():
        ssm.put_parameter(Name=name, Value=value, Type="SecureString")


def _wait_for_object_count(bucket, expected_count):
    object_count_match = _poll_until(lambda: len(list(bucket.objects.all())) >= expected_count)
    assert object_count_match


def _poll_until(function, timeout=30, poll_freq=1):
    elapsed_seconds = 0
    started_time = datetime.now()
    condition_reached = False
    while elapsed_seconds <= timeout and not condition_reached:
        condition_reached = function()
        sleep(poll_freq)
        elapsed_seconds = (datetime.now() - started_time).seconds
    return condition_reached


def test_mesh_inbox_s3_forwarder(tmpdir):
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_DEFAULT_REGION"] = "us-west-1"

    fake_mesh_data_dir = path.join(tmpdir, "mesh")
    fake_mesh = _build_fake_mesh(fake_mesh_data_dir)

    fake_mesh.start()
    fake_aws = _build_fake_aws()
    fake_aws.start()

    mesh = _build_mesh_client()
    s3 = _build_s3_resource()
    ssm = _build_ssm_client()
    _populate_ssm_params(ssm)

    bucket = s3.Bucket(S3_BUCKET)
    bucket.create()
    s3.meta.client.get_waiter("bucket_exists").wait(Bucket=S3_BUCKET)

    forwarder_home_dir = path.join(tmpdir, "forwarder")
    mkdir(forwarder_home_dir)

    file_contents = bytes(a_string(), "utf-8")
    try:
        forwarder = _build_forwarder(forwarder_home_dir)
        forwarder.start()

        mesh.send_message(RECEIVING_MESH_MAILBOX, file_contents)
        _wait_for_object_count(bucket, expected_count=1)
        actual_object = next(iter(bucket.objects.all()))
        assert re.match(r"\d{4}/\d{2}/\d{2}/\d{20}_\d+\.dat", actual_object.key)
        actual_file_contents = actual_object.get()["Body"].read()
        assert actual_file_contents == file_contents
        forwarder.stop()
    finally:
        fake_mesh.stop()
        fake_aws.stop()
