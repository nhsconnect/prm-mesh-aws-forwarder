from argparse import Namespace

from s3mesh.main import parse_arguments


def test_parse_arguments():
    args = [
        "--mesh-mailbox",
        "test-mesh-mailbox",
        "--mesh-password",
        "password",
        "--mesh-url",
        "nice-mesh.biz",
        "--mesh-shared-key",
        "coolkey",
        "--mesh-client-cert-path",
        "path/to/cert.pem",
        "--mesh-client-key-path",
        "path/to/ca/cart.pem",
        "--mesh-ca-cert-path",
        "path/to/ca/cert.pem",
        "--s3-bucket-name",
        "mesh-data-bucket",
    ]

    expected = Namespace(
        mesh_mailbox="test-mesh-mailbox",
        mesh_password="password",
        mesh_url="nice-mesh.biz",
        mesh_shared_key=b"coolkey",
        mesh_client_cert_path="path/to/cert.pem",
        mesh_client_key_path="path/to/ca/cart.pem",
        mesh_ca_cert_path="path/to/ca/cert.pem",
        s3_bucket_name="mesh-data-bucket",
        s3_endpoint_url=None,
        poll_frequency=10,
    )

    actual = parse_arguments(args)

    assert actual == expected
