from os import environ
from unittest.mock import patch

from s3mesh.config import ForwarderConfig


def test_read_config_from_environment():
    environment = {
        "MESH_URL": "nice-mesh.biz",
        "MESH_MAILBOX_SSM_PARAM_NAME": "test-mesh-mailbox",
        "MESH_PASSWORD_SSM_PARAM_NAME": "password",
        "MESH_SHARED_KEY_SSM_PARAM_NAME": "coolkey",
        "MESH_CLIENT_CERT_SSM_PARAM_NAME": "path/to/cert.pem",
        "MESH_CLIENT_KEY_SSM_PARAM_NAME": "path/to/key.pem",
        "MESH_CA_CERT_SSM_PARAM_NAME": "path/to/ca/cert.pem",
        "S3_BUCKET_NAME": "mesh-data-bucket",
        "POLL_FREQUENCY": "60",
        "FORWARDER_HOME": "/home/mesh-forwarder",
    }

    expected_config = ForwarderConfig(
        mesh_url="nice-mesh.biz",
        mesh_mailbox_ssm_param_name="test-mesh-mailbox",
        mesh_password_ssm_param_name="password",
        mesh_shared_key_ssm_param_name="coolkey",
        mesh_client_cert_ssm_param_name="path/to/cert.pem",
        mesh_client_key_ssm_param_name="path/to/key.pem",
        mesh_ca_cert_ssm_param_name="path/to/ca/cert.pem",
        s3_bucket_name="mesh-data-bucket",
        poll_frequency="60",
        forwarder_home="/home/mesh-forwarder",
    )

    with patch.dict(environ, environment):
        actual_config = ForwarderConfig.from_environment_variables()

    assert actual_config == expected_config
