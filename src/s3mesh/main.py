import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Optional

import boto3

from s3mesh.forwarder import MeshToS3Forwarder
from s3mesh.mesh import MeshInbox
from s3mesh.s3 import S3Uploader
from s3mesh.service import MeshToS3ForwarderService
import mesh_client
import logging

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
    args = parse_arguments(sys.argv[1:])

    forwarder_service = build_forwarder_service(
        mesh_config=MeshConfig(
            url=args.mesh_url,
            mailbox=args.mesh_mailbox,
            password=args.mesh_password,
            shared_key=args.mesh_shared_key,
            client_cert_path=args.mesh_client_cert_path,
            client_key_path=args.mesh_client_key_path,
            ca_cert_path=args.mesh_ca_cert_path,
        ),
        s3_config=S3Config(
            bucket_name=args.s3_bucket_name,
            endpoint_url=args.s3_endpoint_url,
        ),
        poll_frequency_sec=args.poll_frequency,
    )

    forwarder_service.start()


def utf8_bytes(value):
    return bytes(value, "utf-8")


def parse_arguments(argument_list):
    parser = ArgumentParser(description="MESH to S3 Forwarder")
    parser.add_argument("--mesh-mailbox", type=str, required=True)
    parser.add_argument("--mesh-password", type=str, required=True)
    parser.add_argument("--mesh-url", type=str, required=True)
    parser.add_argument("--mesh-shared-key", type=utf8_bytes, required=True)
    parser.add_argument("--mesh-client-cert-path", type=str, required=True)
    parser.add_argument("--mesh-client-key-path", type=str, required=True)
    parser.add_argument("--mesh-ca-cert-path", type=str, required=True)
    parser.add_argument("--s3-bucket-name", type=str, required=True)
    parser.add_argument("--s3-endpoint-url", type=str, required=False, default=None)
    parser.add_argument("--poll-frequency", type=int, required=False, default=10)

    return parser.parse_args(argument_list)


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
    endpoint_url: Optional[str]


def build_forwarder_service(
    mesh_config: MeshConfig,
    s3_config: S3Config,
    poll_frequency_sec,
) -> MeshToS3ForwarderService:
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
