from logging import Logger, getLogger
from typing import Dict

logger = getLogger(__name__)


class LoggingProbe:
    def start_observation(self, event_name):
        return LoggingObservation(event_name, logger)


class LoggingObservation:
    def __init__(self, event_name: str, logger: Logger):
        self._logger = logger
        self._event_name = event_name
        self._fields: Dict[str, str] = {"event": event_name}

    def add_field(self, name: str, value: str):
        self._fields[name] = value

    def finish(self):
        self._logger.info(f"Observed {self._event_name}", extra=self._fields)
