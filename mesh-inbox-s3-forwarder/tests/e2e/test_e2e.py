import ssl
from os import path, environ
from threading import Thread

import boto3
import mesh_client
from fake_mesh import FakeMeshApplication
from cheroot.ssl.builtin import BuiltinSSLAdapter
from cheroot.wsgi import Server
from freezegun import freeze_time
from moto.server import DomainDispatcherApplication, create_backend_app
from s3mesh.main import build_forwarder_service, MeshConfig, S3Config

from tests.builders.common import a_string, a_datetime


def bundled_file(filename):
    return path.join(path.dirname(mesh_client.__file__), filename)


CA_CERT = bundled_file("ca.cert.pem")
SERVER_CERT = bundled_file("server.cert.pem")
SERVER_KEY = bundled_file("server.key.pem")
CLIENT_CERT = bundled_file("client.cert.pem")
CLIENT_KEY = bundled_file("client.key.pem")

FAKE_MESH_HOST = "127.0.0.1"
FAKE_MESH_PORT = 8829
FAKE_MESH_URL = f"https://localhost:{FAKE_MESH_PORT}"
FAKE_MESH_SHARED_KEY = bytes(a_string(), "utf-8")
FAKE_MESH_CLIENT_PASSWORD = a_string()

FAKE_S3_HOST = "127.0.0.1"
FAKE_S3_PORT = 8887
FAKE_S3_URL = f"http://127.0.0.1:{FAKE_S3_PORT}"

SENDING_MESH_MAILBOX = "e2e-test-mailbox-sender"
RECEIVING_MESH_MAILBOX = "e2e-test-mailbox-receiver"
S3_BUCKET = "e2e-test-bucket"

WAIT_60_SEC = {"Delay": 5, "MaxAttempts": 12}
frozen_time = a_datetime()


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
    app = FakeMeshApplication(mesh_dir, FAKE_MESH_SHARED_KEY, FAKE_MESH_CLIENT_PASSWORD)
    httpd = Server((FAKE_MESH_HOST, FAKE_MESH_PORT), app)

    server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=CA_CERT)
    server_context.load_cert_chain(SERVER_CERT, SERVER_KEY)
    server_context.check_hostname = False
    server_context.verify_mode = ssl.CERT_REQUIRED

    ssl_adapter = BuiltinSSLAdapter(SERVER_CERT, SERVER_KEY, CA_CERT)
    ssl_adapter.context = server_context
    httpd.ssl_adapter = ssl_adapter
    return ThreadedHttpd(httpd)


def _build_fake_s3():
    app = DomainDispatcherApplication(create_backend_app, "s3")
    httpd = Server((FAKE_S3_HOST, FAKE_S3_PORT), app)
    return ThreadedHttpd(httpd)


def _build_forwarder():
    forwarder = build_forwarder_service(
        mesh_config=MeshConfig(
            url=FAKE_MESH_URL,
            mailbox=RECEIVING_MESH_MAILBOX,
            password=FAKE_MESH_CLIENT_PASSWORD,
            shared_key=FAKE_MESH_SHARED_KEY,
            client_cert_path=CLIENT_CERT,
            client_key_path=CLIENT_KEY,
            ca_cert_path=CA_CERT,
        ),
        s3_config=S3Config(
            bucket_name=S3_BUCKET,
            endpoint_url=FAKE_S3_URL,
        ),
        poll_frequency_sec=5,
    )
    return ThreadedForwarder(forwarder)


def _build_mesh_client():
    return mesh_client.MeshClient(
        FAKE_MESH_URL,
        SENDING_MESH_MAILBOX,
        FAKE_MESH_CLIENT_PASSWORD,
        shared_key=FAKE_MESH_SHARED_KEY,
        cert=(CLIENT_CERT, CLIENT_KEY),
        verify=CA_CERT,
    )


def _build_s3_client():
    return boto3.client(
        service_name="s3",
        endpoint_url=FAKE_S3_URL,
    )


@freeze_time(frozen_time)
def test_mesh_inbox_s3_forwarder(tmpdir):
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_DEFAULT_REGION"] = "us-west-1"

    fake_mesh = _build_fake_mesh(path.join(tmpdir, "mesh"))

    fake_mesh.start()
    fake_s3 = _build_fake_s3()
    fake_s3.start()

    forwarder = _build_forwarder()

    mesh = _build_mesh_client()
    s3 = _build_s3_client()

    s3.create_bucket(Bucket=S3_BUCKET)
    s3.get_waiter("bucket_exists").wait(Bucket=S3_BUCKET)

    forwarder.start()

    file_contents = bytes(a_string(), "utf-8")

    try:
        mesh.send_message(RECEIVING_MESH_MAILBOX, file_contents)
        expected_key = frozen_time.strftime("%Y/%m/%d/%Y%m%d%H%M%S_000000000.dat")
        s3.get_waiter("object_exists").wait(
            Bucket=S3_BUCKET, Key=expected_key, WaiterConfig=WAIT_60_SEC
        )
        actual_object = s3.get_object(Bucket=S3_BUCKET, Key=expected_key)
        actual_file_contents = actual_object["Body"].read()
        assert actual_file_contents == file_contents
    finally:
        fake_mesh.stop()
        fake_s3.stop()
        forwarder.stop()
