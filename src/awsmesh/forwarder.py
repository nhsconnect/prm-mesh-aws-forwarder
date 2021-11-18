import logging

from awsmesh.mesh import InvalidMeshHeader, MeshClientNetworkError, MeshInbox, MissingMeshHeader
from awsmesh.monitoring.probe import LoggingProbe
from awsmesh.uploader import MessageUploader, UploaderError

logger = logging.getLogger(__name__)


class RetryableException(Exception):
    pass


class MeshToAwsForwarder:
    def __init__(
        self,
        inbox: MeshInbox,
        uploader: MessageUploader,
        probe: LoggingProbe,
        disable_message_header_validation,
    ):
        self._inbox = inbox
        self._uploader = uploader
        self._probe = probe
        self._disable_message_header_validation = disable_message_header_validation

    def forward_messages(self):
        for message in self._poll_messages():
            self._process_message(message)

    def is_mailbox_empty(self):
        count_message_event = self._probe.new_count_messages_event()
        try:
            message_count = self._inbox.count_messages()
            count_message_event.record_message_count(message_count)
            return message_count == 0
        except MeshClientNetworkError as e:
            count_message_event.record_mesh_client_network_error(e)
            raise RetryableException()
        finally:
            count_message_event.finish()

    def _poll_messages(self):
        poll_inbox_event = self._probe.new_poll_inbox_event()
        try:
            messages = self._inbox.read_messages()
            poll_inbox_event.record_message_batch_count(len(messages))
            return messages
        except MeshClientNetworkError as e:
            poll_inbox_event.record_mesh_client_network_error(e)
            raise RetryableException()
        finally:
            poll_inbox_event.finish()

    # flake8: noqa: C901
    def _process_message(self, message):
        forward_message_event = self._probe.new_forward_message_event()
        try:
            forward_message_event.record_message_metadata(message)
            if not self._disable_message_header_validation:
                message.validate()
            self._uploader.upload(message, forward_message_event)
            message.acknowledge()
        except MissingMeshHeader as e:
            forward_message_event.record_missing_mesh_header(e)
        except InvalidMeshHeader as e:
            forward_message_event.record_invalid_mesh_header(e)
        except UploaderError as e:
            forward_message_event.record_uploader_error(e)
        except MeshClientNetworkError as e:
            forward_message_event.record_mesh_client_network_error(e)
            raise RetryableException()
        finally:
            forward_message_event.finish()