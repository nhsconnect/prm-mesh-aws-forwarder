from s3mesh.mesh import MeshMessage

FORWARD_MESSAGE_EVENT = "FORWARD_MESH_MESSAGE"


class ForwardMessageEvent:
    def __init__(self, output):
        self._fields = {}
        self._output = output

    def record_message_metadata(self, message: MeshMessage):
        self._fields["messageId"] = message.id
        self._fields["sender"] = message.sender
        self._fields["recipient"] = message.recipient
        self._fields["fileName"] = message.file_name

    def finish(self):
        self._output.log_event(FORWARD_MESSAGE_EVENT, self._fields)
