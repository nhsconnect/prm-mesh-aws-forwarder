POLL_INBOX_EVENT = "POLL_MESSAGE"


class PollInboxEvent:
    def __init__(self, output):
        self._fields = {}
        self._output = output

    def finish(self):
        self._output.log_event(POLL_INBOX_EVENT, self._fields)
