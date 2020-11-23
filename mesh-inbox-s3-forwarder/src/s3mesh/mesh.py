from typing import Iterable

from mesh_client import MeshClient, Message


class MeshMessage:
    def __init__(self, client_message: Message):
        self.id: str = client_message.id()
        self._client_message: Message = client_message
        self.filename: str = client_message.mex_header("filename")
        self.date_delivered: str = client_message.mex_header("statustimestamp")

    def acknowledge(self):
        self._client_message.acknowledge()

    def read(self):
        self._client_message.read()


class MeshInbox:
    def __init__(self, client: MeshClient):
        self._client = client

    def read_messages(self) -> Iterable[MeshMessage]:
        for client_message in self._client.iterate_all_messages():
            yield MeshMessage(client_message)
