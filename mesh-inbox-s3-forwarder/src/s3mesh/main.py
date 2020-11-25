from dataclasses import dataclass

from s3mesh.service import MeshToS3ForwarderService


def main():
    print("hello mesh world!")  # noqa: T001


@dataclass
class MeshConfig:
    url: str
    mailbox: str
    password: str
    shared_key: bytes
    client_cert_path: str
    client_key_path: str
    ca_cert_path: str


@dataclass
class S3Config:
    bucket_name: str
    endpoint_url: str


def build_forwarder_service(
    mesh_config: MeshConfig,
    s3_config: S3Config,
    poll_frequency_sec,
):
    return MeshToS3ForwarderService(None)
