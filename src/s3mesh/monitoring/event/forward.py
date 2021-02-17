FORWARD_MESSAGE_EVENT = "FORWARD_MESH_MESSAGE"


class ForwardMessageEvent:
    def __init__(self, output):
        self._fields = {}
        self._output = output

    def finish(self):
        self._output.log_event(FORWARD_MESSAGE_EVENT, self._fields)
