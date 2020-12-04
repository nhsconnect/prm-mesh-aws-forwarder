from datetime import datetime
from typing import Iterable

from mesh_client import MeshClient, Message


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
            except InvalidMeshHeader:
                pass


class InvalidMeshHeader(Exception):
    pass


class UnexpectedStatusEvent(InvalidMeshHeader):
    def __init__(self, message_id, status_event_header):
        super().__init__("Unexpected status event header")
        self.message_id = message_id
        self.status_event_header = status_event_header


class UnsuccessfulStatus(InvalidMeshHeader):
    def __init__(self, message_id, status_success_header):
        super().__init__("Unsuccessful status header")
        self.message_id = message_id
        self.status_success_header = status_success_header


class UnexpectedMessageType(InvalidMeshHeader):
    def __init__(self, message_id, message_type_header):
        super().__init__("Unexpected message type header")
        self.message_id = message_id
        self.message_type_header = message_type_header
