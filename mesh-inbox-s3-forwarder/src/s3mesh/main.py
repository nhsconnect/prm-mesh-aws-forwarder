from dataclasses import dataclass

import boto3

from s3mesh.forwarder import MeshToS3Forwarder
from s3mesh.mesh import MeshInbox
from s3mesh.s3 import S3Uploader
from s3mesh.service import MeshToS3ForwarderService
import mesh_client


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
    s3 = boto3.client(service_name="s3", endpoint_url=s3_config.endpoint_url)
    uploader = S3Uploader(s3, s3_config.bucket_name)

    mesh = mesh_client.MeshClient(
        mesh_config.url,
        mesh_config.mailbox,
        mesh_config.password,
        shared_key=mesh_config.shared_key,
        cert=(mesh_config.client_cert_path, mesh_config.client_key_path),
        verify=mesh_config.ca_cert_path,
    )
    inbox = MeshInbox(mesh)
    forwarder = MeshToS3Forwarder(inbox, uploader)
    return MeshToS3ForwarderService(forwarder, poll_frequency_sec)
