from logging import Logger, getLogger

from s3mesh.monitoring.event.count import CountMessagesEvent
from s3mesh.monitoring.output import LoggingOutput
from s3mesh.probe import LoggingObservation

logger = getLogger(__name__)


class LoggingProbe:
    def __init__(self, log: Logger = logger):
        self._output = LoggingOutput(log)

    def new_count_messages_event(self) -> CountMessagesEvent:
        return CountMessagesEvent(self._output)

    def start_observation(self, event_name):
        return LoggingObservation(event_name, logger)
