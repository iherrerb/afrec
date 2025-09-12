from __future__ import annotations

import json
import os
import socket
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


def _get_ip() -> str:
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        for ip in ips:
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    return "127.0.0.1"


@dataclass
class Session:
    id: str
    actor: str
    started_at: str  # ISO8601 UTC
    ip_address: str

    @staticmethod
    def start(actor: str | None = None) -> "Session":
        sid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        return Session(
            id=sid,
            actor=actor or os.getenv("USER") or os.getenv("USERNAME") or "unknown",
            started_at=now,
            ip_address=_get_ip(),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, ensure_ascii=False, indent=2)
