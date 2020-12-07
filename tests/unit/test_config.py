from os import environ
from unittest import mock

from s3mesh.config import ForwarderConfig


def test_read_config_from_environment():
    environment = {
        "MESH_URL": "nice-mesh.biz",
        "MESH_MAILBOX_SSM_PARAM_NAME": "/params/mesh/mailbox",
        "MESH_PASSWORD_SSM_PARAM_NAME": "/params/mesh/password",
        "MESH_SHARED_KEY_SSM_PARAM_NAME": "/params/mesh/shared-key",
        "MESH_CLIENT_CERT_SSM_PARAM_NAME": "/params/mesh/client-cert",
        "MESH_CLIENT_KEY_SSM_PARAM_NAME": "/params/mesh/client-key",
        "MESH_CA_CERT_SSM_PARAM_NAME": "/params/mesh/ca-cert",
        "S3_BUCKET_NAME": "mesh-data-bucket",
        "POLL_FREQUENCY": "60",
        "FORWARDER_HOME": "/home/mesh-forwarder",
    }

    expected_config = ForwarderConfig(
        mesh_url="nice-mesh.biz",
        mesh_mailbox_ssm_param_name="/params/mesh/mailbox",
        mesh_password_ssm_param_name="/params/mesh/password",
        mesh_shared_key_ssm_param_name="/params/mesh/shared-key",
        mesh_client_cert_ssm_param_name="/params/mesh/client-cert",
        mesh_client_key_ssm_param_name="/params/mesh/client-key",
        mesh_ca_cert_ssm_param_name="/params/mesh/ca-cert",
        s3_bucket_name="mesh-data-bucket",
        poll_frequency="60",
        forwarder_home="/home/mesh-forwarder",
    )

    with mock.patch.dict(environ, environment):
        actual_config = ForwarderConfig.from_environment_variables()

    assert actual_config == expected_config


@mock.patch("sys.exit")
def test_read_config_from_environment_calls_exit_when_missing_variable(mock_exit):
    with mock.patch.dict(environ, {}, clear=True):
        ForwarderConfig.from_environment_variables()

    mock_exit.assert_called_with(1)
