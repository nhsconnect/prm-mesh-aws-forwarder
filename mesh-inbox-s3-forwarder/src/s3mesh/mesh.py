from typing import Iterable

from mesh_client import MeshClient, Message


class MeshMessage:
    def __init__(self, client_message: Message):
        self.id = client_message.id()

    def acknowledge(self):
        raise NotImplementedError


class MeshInbox:
    def __init__(self, client: MeshClient):
        self._client = client

    def read_messages(self) -> Iterable[MeshMessage]:
        for client_message in self._client.iterate_all_messages():
            yield MeshMessage(client_message)
