import json
from logging import LogRecord


class JsonFormatter:
    def format(self, record: LogRecord) -> str:
        base = {
            "level": record.levelname,
            "module": record.module,
            "message": record.msg,
        }

        return json.dumps(base)
