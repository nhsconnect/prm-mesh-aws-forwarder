from logging import Logger, getLogger
from typing import Dict

logger = getLogger(__name__)


class LoggingProbe:
    def start_observation(self, name):
        return LoggingObservation(name, logger)


class LoggingObservation:
    def __init__(self, name: str, logger: Logger):
        self._logger = logger
        self._name = name
        self._fields: Dict[str, str] = {}

    def add_field(self, name: str, value: str):
        self._fields[name] = value

    def finish(self):
        self._logger.info(self._name, extra=self._fields)
