from logging import Logger


class LoggingOutput:
    def __init__(self, log: Logger):
        self._logger = log

    def log_event(self, event_name: str, fields: dict):
        extra_fields = {**fields, "event": event_name}
        self._logger.info(f"Observed {event_name}", extra=extra_fields)
