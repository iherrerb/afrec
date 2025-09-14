""" Aquí se Gestiona la exploración del espacio de archivos en Dropbox (files/list_folder).
Permite:
* Listado recursivo de carpetas.
* Filtrado por extensión y rango de fechas.
* Generación de inventarios (inventario.json, inventario.csv).
* Cada elemento incluye metadatos: nombre, ruta, tamaño, fechas, hash remoto (content_hash).
Es la base del inventario lógico de evidencias. """

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from dateutil import parser as dtparser
from dropbox import Dropbox
from dropbox import files as dbx_files


@dataclass
class InventoryItem:
    path_display: str
    id: str
    size: int
    client_modified: str
    server_modified: str
    rev: str
    content_hash: str | None


def _parse_date(d: str | None) -> Optional[datetime]:
    if not d:
        return None
    return dtparser.parse(d)


def _ext_matches(path: str, exts: Optional[Sequence[str]]) -> bool:
    if not exts:
        return True
    p = Path(path.lower())
    return p.suffix in {e.lower().strip() if e.startswith(".") else "." + e.lower().strip() for e in exts}


def _date_in_range(server_modified: datetime, date_from: Optional[datetime], date_to: Optional[datetime]) -> bool:
    if date_from and server_modified < date_from:
        return False
    if date_to and server_modified > date_to:
        return False
    return True


def list_inventory(
    dbx: Dropbox,
    root: str = "/",
    exts: Optional[Sequence[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[InventoryItem]:
    from_dt = _parse_date(date_from)
    to_dt = _parse_date(date_to)

    result = dbx.files_list_folder(root, recursive=True, include_non_downloadable_files=True, limit=2000)
    items: List[InventoryItem] = []

    def handle_entries(entries: Iterable[dbx_files.Metadata]) -> None:
        for entry in entries:
            if isinstance(entry, dbx_files.FileMetadata):
                if not _ext_matches(entry.path_display, exts):
                    continue
                if not _date_in_range(entry.server_modified, from_dt, to_dt):
                    continue
                items.append(
                    InventoryItem(
                        path_display=entry.path_display,
                        id=entry.id,
                        size=entry.size,
                        client_modified=entry.client_modified.isoformat(),
                        server_modified=entry.server_modified.isoformat(),
                        rev=entry.rev,
                        content_hash=getattr(entry, "content_hash", None),
                    )
                )

    handle_entries(result.entries)
    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        handle_entries(result.entries)
    return items


def save_inventory_json(items: List[InventoryItem], out_file: Path) -> None:
    import json
    out_file.parent.mkdir(parents=True, exist_ok=True)
    data = [asdict(i) for i in items]
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def save_inventory_csv(items: List[InventoryItem], out_file: Path) -> None:
    import csv
    out_file.parent.mkdir(parents=True, exist_ok=True)
    headers = ["path_display", "id", "size", "client_modified", "server_modified", "rev", "content_hash"]
    with open(out_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for i in items:
            writer.writerow(asdict(i))
