from typing import Iterable
from s3mesh.mesh import MeshInbox, MeshMessage
from s3mesh.s3 import S3Uploader


class MeshToS3Forwarder:
    def __init__(self, inbox: MeshInbox, uploader: S3Uploader):
        self._inbox = inbox
        self._uploader = uploader

    def forward_messages(self):
        messages: Iterable[MeshMessage] = self._inbox.read_messages()
        for message in messages:
            self._uploader.upload(message)
            message.acknowledge()
