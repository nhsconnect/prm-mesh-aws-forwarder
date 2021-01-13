import logging

from s3mesh.mesh import InvalidMeshHeader, MeshClientNetworkError, MeshInbox, MissingMeshHeader
from s3mesh.probe import LoggingProbe
from s3mesh.s3 import S3Uploader

INVALID_MESH_HEADER_ERROR = "INVALID_MESH_HEADER"
MISSING_MESH_HEADER_ERROR = "MISSING_MESH_HEADER"
MESH_CLIENT_NETWORK_ERROR = "MESH_CLIENT_NETWORK_ERROR"
FORWARD_MESSAGE_EVENT = "FORWARD_MESH_MESSAGE"
POLL_MESSAGE_EVENT = "POLL_MESSAGE"

logger = logging.getLogger(__name__)


class RetryableException(Exception):
    def __init__(self, message=None):
        self.error_message = message


class MeshToS3Forwarder:
    def __init__(self, inbox: MeshInbox, uploader: S3Uploader, probe: LoggingProbe):
        self._inbox = inbox
        self._uploader = uploader
        self._probe = probe

    def forward_messages(self):
        for message in self._poll_messages():
            self._process_message(message)

    def is_mailbox_empty(self):
        try:
            return self._inbox.count_messages() == 0
        except MeshClientNetworkError as e:
            raise RetryableException(e.error_message)

    def _poll_messages(self):
        observation = self._new_poll_message_observation()
        try:
            messages = self._inbox.read_messages()
            observation.add_field("polledMessages", len(messages))
            return messages
        except MeshClientNetworkError as e:
            observation.add_field("error", MESH_CLIENT_NETWORK_ERROR)
            observation.add_field("errorMessage", e.error_message)
            raise RetryableException(e.error_message)
        finally:
            observation.finish()

    def _new_forwarded_message_observation(self, message):
        observation = self._probe.start_observation(FORWARD_MESSAGE_EVENT)
        observation.add_field("messageId", message.id)
        return observation

    def _new_poll_message_observation(self):
        observation = self._probe.start_observation(POLL_MESSAGE_EVENT)
        return observation

    def _process_message(self, message):
        observation = self._new_forwarded_message_observation(message)
        try:
            observation.add_field("sender", message.sender)
            observation.add_field("recipient", message.recipient)
            observation.add_field("fileName", message.file_name)
            message.validate()
            self._uploader.upload(message, observation)
            message.acknowledge()
        except MissingMeshHeader as e:
            observation.add_field("error", MISSING_MESH_HEADER_ERROR)
            observation.add_field("missingHeaderName", e.header_name)
        except InvalidMeshHeader as e:
            observation.add_field("error", INVALID_MESH_HEADER_ERROR)
            observation.add_field("expectedHeaderValue", e.expected_header_value)
            observation.add_field("receivedHeaderValue", e.header_value)
        except MeshClientNetworkError as e:
            observation.add_field("error", MESH_CLIENT_NETWORK_ERROR)
            observation.add_field("errorMessage", e.error_message)
            raise RetryableException(e.error_message)
        finally:
            observation.finish()
