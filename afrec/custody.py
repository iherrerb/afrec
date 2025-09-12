from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


@dataclass
class CustodyEntry:
    ts: str
    actor: str
    action: str
    details: Dict[str, Any]

    @staticmethod
    def create(actor: str, action: str, **details: Any) -> "CustodyEntry":
        return CustodyEntry(
            ts=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            action=action,
            details=details,
        )


class ChainOfCustody:
    def __init__(self, file: Path) -> None:
        self.file = file
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: CustodyEntry) -> None:
        with open(self.file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
