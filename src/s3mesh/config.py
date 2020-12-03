import logging
import sys
from dataclasses import dataclass, fields
from os import environ

logger = logging.getLogger(__name__)


def read_env(env_var):
    if env_var not in environ:
        logger.error(f"Expected environment variable {env_var} was not set, exiting...")
        sys.exit(1)
    else:
        return environ[env_var]


@dataclass
class ForwarderConfig:
    mesh_url: str
    mesh_mailbox_ssm_param_name: str
    mesh_password_ssm_param_name: str
    mesh_shared_key_ssm_param_name: str
    mesh_client_cert_ssm_param_name: str
    mesh_client_key_ssm_param_name: str
    mesh_ca_cert_ssm_param_name: str
    s3_bucket_name: str
    poll_frequency: str
    forwarder_home: str

    @classmethod
    def from_environment_variables(cls):
        return cls(**{field.name: read_env(field.name.upper()) for field in fields(cls)})
