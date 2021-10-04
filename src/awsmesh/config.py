import logging
import sys
from dataclasses import MISSING, dataclass, fields
from typing import Optional

logger = logging.getLogger(__name__)


def _read_env(field, env_vars):
    env_var = field.name.upper()
    if env_var in env_vars:
        return env_vars[env_var]
    elif field.default != MISSING:
        return field.default
    else:
        logger.error(f"Expected environment variable {env_var} was not set, exiting...")
        sys.exit(1)


@dataclass
class ForwarderConfig:
    mesh_url: str
    mesh_mailbox_ssm_param_name: str
    mesh_password_ssm_param_name: str
    mesh_shared_key_ssm_param_name: str
    mesh_client_cert_ssm_param_name: str
    mesh_client_key_ssm_param_name: str
    mesh_ca_cert_ssm_param_name: str
    poll_frequency: str
    forwarder_home: str
    message_destination: str = "s3"
    s3_bucket_name: Optional[str] = None
    sns_topic_arn: Optional[str] = None
    endpoint_url: Optional[str] = None
    ssm_endpoint_url: Optional[str] = None

    @classmethod
    def from_environment_variables(cls, env_vars):
        return cls(**{field.name: _read_env(field, env_vars) for field in fields(cls)})
