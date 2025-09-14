""" Aquí se Maneja la descarga controlada de archivos desde Dropbox (files/download).
Incluye un sistema de reintentos automáticos en caso de fallos o rate limits.
Guarda cada archivo en la carpeta cases/.../evidence/.
Tras cada descarga, genera registros de integridad con integrity.py.
Garantiza descargas completas y confiables. """

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Iterable, List

from dropbox import Dropbox
from dropbox.exceptions import ApiError

from .integrity import build_hash_record


def _retry(fn, *, retries: int = 5, base_delay: float = 1.0):
    last = None
    for attempt in range(retries):
        try:
            return fn()
        except ApiError as e:
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
            last = e
        except Exception as e:  # pragma: no cover
            last = e
            time.sleep(base_delay * (2 ** attempt))
    if last:
        raise last


def download_files(
    dbx: Dropbox,
    items: Iterable[Dict[str, str | int | None]],
    evidence_root: Path,
) -> List[Dict[str, str | int | None]]:
    evidence_root.mkdir(parents=True, exist_ok=True)
    hash_records: List[Dict[str, str | int | None]] = []
    for i in items:
        path_display = str(i["path_display"])
        dropbox_path = path_display
        local_path = evidence_root / path_display.strip("/")
        local_path.parent.mkdir(parents=True, exist_ok=True)

        def _dl():
            dbx.files_download_to_file(str(local_path), dropbox_path)

        _retry(_dl, retries=6, base_delay=1.5)
        rec = build_hash_record(local_path, i)
        hash_records.append(rec)
    return hash_records
