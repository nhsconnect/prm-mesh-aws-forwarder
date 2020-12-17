from logging import Logger, getLogger
from typing import Dict

logger = getLogger(__name__)


class LoggingProbe:
    def start_observation(self):
        return LoggingObservation(logger)


class LoggingObservation:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._fields: Dict[str, str] = {}

    def add_field(self, name: str, value: str):
        self._fields[name] = value

    def finish(self):
        self._logger.info("Message", extra=self._fields)
