import json
from datetime import datetime
from logging import LogRecord


def _convert_timestamp_to_iso(timestamp: float) -> str:
    return datetime.utcfromtimestamp(timestamp).isoformat()


class JsonFormatter:
    def format(self, record: LogRecord) -> str:
        base = {
            "level": record.levelname,
            "module": record.module,
            "message": record.msg,
            "time": _convert_timestamp_to_iso(record.created),
        }

        return json.dumps(base)
