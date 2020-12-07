import logging
from datetime import datetime
from typing import Iterable

from mesh_client import MeshClient, Message

logger = logging.getLogger(__name__)


class MeshMessage:
    def __init__(self, client_message: Message):
        self.id: str = client_message.id()
        self._client_message: Message = client_message
        self.file_name: str = client_message.mex_header("filename")
        self.date_delivered: datetime = datetime.strptime(
            client_message.mex_header("statustimestamp"), "%Y%m%d%H%M%S"
        )
        self._validate_message()

    def _validate_message(self):
        if self._client_message.mex_header("statusevent") != "TRANSFER":
            raise UnexpectedStatusEvent(self.id, self._client_message.mex_header("statusevent"))
        if self._client_message.mex_header("statussuccess") != "SUCCESS":
            raise UnsuccessfulStatus(self.id, self._client_message.mex_header("statussuccess"))
        if self._client_message.mex_header("messagetype") != "DATA":
            raise UnexpectedMessageType(self.id, self._client_message.mex_header("messagetype"))

    def acknowledge(self):
        self._client_message.acknowledge()

    def read(self, n=None):
        return self._client_message.read(n)


class MeshInbox:
    def __init__(self, client: MeshClient):
        self._client = client

    def read_messages(self) -> Iterable[MeshMessage]:
        for client_message in self._client.iterate_all_messages():
            try:
                yield MeshMessage(client_message)
            except InvalidMeshHeader as e:
                logger.warning(
                    f"Message {e.message_id}: "
                    f"Invalid MESH {e.header_name} header - expected: {e.expected_header_value}, "
                    f"instead got: {e.header_value}"
                )


class InvalidMeshHeader(Exception):
    def __init__(
        self, header_name: str, message_id: str, header_value: str, expected_header_value: str
    ):
        self.message_id = message_id
        self.header_name = header_name
        self.header_value = header_value
        self.expected_header_value = expected_header_value


class UnexpectedStatusEvent(InvalidMeshHeader):
    def __init__(self, message_id, status_event_header):
        super().__init__(
            header_name="statusevent",
            message_id=message_id,
            header_value=status_event_header,
            expected_header_value="TRANSFER",
        )


class UnsuccessfulStatus(InvalidMeshHeader):
    def __init__(self, message_id, status_success_header):
        super().__init__(
            header_name="statussuccess",
            message_id=message_id,
            header_value=status_success_header,
            expected_header_value="SUCCESS",
        )


class UnexpectedMessageType(InvalidMeshHeader):
    def __init__(self, message_id, message_type_header):
        super().__init__(
            header_name="messagetype",
            message_id=message_id,
            header_value=message_type_header,
            expected_header_value="DATA",
        )
