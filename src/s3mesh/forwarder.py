import logging
from dataclasses import dataclass
from threading import Event
from typing import Iterable, Optional

import boto3
import mesh_client

from s3mesh.mesh import InvalidMeshHeader, MeshInbox, MeshMessage, MissingMeshHeader
from s3mesh.s3 import S3Uploader

logger = logging.getLogger(__name__)


class MeshToS3Forwarder:
    def __init__(self, inbox: MeshInbox, uploader: S3Uploader):
        self._inbox = inbox
        self._uploader = uploader

    def forward_messages(self):
        messages: Iterable[MeshMessage] = self._inbox.read_messages()
        for message in messages:
            self._process_message(message)

    def _process_message(self, message):

        try:
            logger.info(
                "Message received", extra={"messageId": message.id, "fileName": message.file_name}
            )
            message.validate()
            self._uploader.upload(message)
            logger.info("Message uploaded", extra={"messageId": message.id})
            message.acknowledge()
            logger.info("Message acknowledged", extra={"messageId": message.id})
        except MissingMeshHeader as e:
            logger.warning(f"Message {e.message_id}: " f"Missing MESH {e.header_name} header")
        except InvalidMeshHeader as e:
            logger.warning(
                f"Message {e.message_id}: "
                f"Invalid MESH {e.header_name} header - expected: {e.expected_header_value}, "
                f"instead got: {e.header_value}"
            )


class MeshToS3ForwarderService:
    def __init__(self, forwarder: MeshToS3Forwarder, poll_frequency_sec: int):
        self._forwarder = forwarder
        self._exit_requested = Event()
        self._poll_frequency_sec = poll_frequency_sec

    def start(self):
        logger.info("Started forwarder service")
        while not self._exit_requested.is_set():
            self._forwarder.forward_messages()
            self._exit_requested.wait(self._poll_frequency_sec)
        logger.info("Exiting forwarder service")

    def stop(self):
        logger.info("Received request to stop")
        self._exit_requested.set()


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
