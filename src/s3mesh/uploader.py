from typing import Protocol

from s3mesh.mesh import MeshMessage
from s3mesh.monitoring.event.forward import ForwardMessageEvent


class UploaderError(Exception):
    def __init__(self, message):
        self.error_message = message


class MessageUploader(Protocol):
    def upload(self, message: MeshMessage, forward_message_event: ForwardMessageEvent):
        ...
