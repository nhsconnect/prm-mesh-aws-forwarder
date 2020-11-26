from typing import Iterable
from s3mesh.mesh import MeshInbox, MeshMessage
from s3mesh.s3 import S3Uploader
import logging

logger = logging.getLogger(__name__)


class MeshToS3Forwarder:
    def __init__(self, inbox: MeshInbox, uploader: S3Uploader):
        self._inbox = inbox
        self._uploader = uploader

    def forward_messages(self):
        messages: Iterable[MeshMessage] = self._inbox.read_messages()
        for message in messages:
            logger.info(f"Message received: {message.id}")
            self._uploader.upload(message)
            logger.info(f"Message uploaded: {message.id}")
            message.acknowledge()
            logger.info(f"Message acknowledged: {message.id}")
