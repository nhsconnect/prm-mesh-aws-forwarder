from typing import Protocol

from awsmesh.mesh import MeshMessage


class UploaderError(Exception):
    pass


class UploadEventMetadata(Protocol):
    def record_s3_key(self, key):
        ...

    def record_sns_message_id(self, sns_message_id):
        ...


class MessageUploader(Protocol):
    def upload(self, message: MeshMessage, upload_event_metadata: UploadEventMetadata):
        ...
