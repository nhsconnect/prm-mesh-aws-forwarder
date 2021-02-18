from s3mesh.forwarder import MISSING_MESH_HEADER_ERROR
from s3mesh.mesh import MeshMessage, MissingMeshHeader

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

    def record_s3_key(self, key):
        self._fields["s3Key"] = key

    def record_missing_mesh_header(self, exception: MissingMeshHeader):
        self._fields["error"] = MISSING_MESH_HEADER_ERROR
        self._fields["missingHeaderName"] = exception.header_name

    def finish(self):
        self._output.log_event(FORWARD_MESSAGE_EVENT, self._fields)
