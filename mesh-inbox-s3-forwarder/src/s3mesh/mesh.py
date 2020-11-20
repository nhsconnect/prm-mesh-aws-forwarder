from typing import Iterable


class MeshMessage:
    def acknowledge(self):
        pass


class MeshInbox:
    def read_messages(self) -> Iterable[MeshMessage]:
        pass
