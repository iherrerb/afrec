from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        data: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k not in ("args", "msg", "levelname", "levelno", "pathname", "filename",
                         "module", "exc_info", "exc_text", "stack_info", "lineno",
                         "funcName", "created", "msecs", "relativeCreated", "thread",
                         "threadName", "processName", "process", "name"):
                data[k] = v
        return json.dumps(data, ensure_ascii=False)


def setup_logging(log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("afrec")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    if not logger.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(JsonFormatter())
        logger.addHandler(sh)
        if log_file:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(JsonFormatter())
            logger.addHandler(fh)
    return logger
