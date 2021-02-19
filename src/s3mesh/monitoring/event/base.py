from s3mesh.mesh import MeshClientNetworkError
from s3mesh.monitoring.error import MESH_CLIENT_NETWORK_ERROR


class ForwarderEvent:
    def __init__(self, output, event_name):
        self._event_name = event_name
        self._fields = {}
        self._output = output

    def record_mesh_client_network_error(self, exception: MeshClientNetworkError):
        self._fields["error"] = MESH_CLIENT_NETWORK_ERROR
        self._fields["errorMessage"] = exception.error_message

    def finish(self):
        self._output.log_event(self._event_name, self._fields)
