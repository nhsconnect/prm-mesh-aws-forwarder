from dataclasses import dataclass, fields
from os import environ


def read_env(env_var):
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
