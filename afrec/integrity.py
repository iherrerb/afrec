""" Aquí se Calcula hashes de integridad.
Funciones:
* hash_file → SHA-256 o MD5 de un archivo local.
* dropbox_content_hash → implementa el mismo algoritmo de Dropbox para validar descargas.
* build_hash_record → genera un registro con:
* ruta local y en Dropbox,
* hashes locales,
* content_hash remoto,
* comparación (yes/no/n-a).
Confirma que los archivos adquiridos son idénticos a los de Dropbox. """

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional

try:
   from dropbox.dropbox_content_hasher import DropboxContentHasher
except Exception:  # pragma: no cover
   DropboxContentHasher = None  # type: ignore


def hash_file(path: Path, algo: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
    if algo not in {"sha256", "md5"}:
        raise ValueError("Unsupported algorithm")
    h = hashlib.sha256() if algo == "sha256" else hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            data = fh.read(chunk_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def dropbox_content_hash(path: Path, chunk_size: int = 4 * 1024 * 1024) -> Optional[str]:
    """Calcula el content hash de Dropbox para un archivo local."""
    if DropboxContentHasher is not None:
        # Usar helper oficial
        hasher = DropboxContentHasher()
        with open(path, "rb") as fh:
            while True:
                block = fh.read(chunk_size)
                if not block:
                    break
                hasher.update(block)
        return hasher.hexdigest()
    else:
        
        block_hashes = []
        with open(path, "rb") as fh:
            while True:
                block = fh.read(chunk_size)
                if not block:
                    break
                block_hashes.append(hashlib.sha256(block).digest())
        return hashlib.sha256(b"".join(block_hashes)).hexdigest()



def build_hash_record(local_path: Path, remote: Dict[str, str | int | None]) -> Dict[str, str | int | None]:
    sha256 = hash_file(local_path, "sha256")
    md5 = hash_file(local_path, "md5")
    dbx_hash = dropbox_content_hash(local_path)
    rec: Dict[str, str | int | None] = {
        "path_local": str(local_path),
        "path_dropbox": remote.get("path_display"),
        "size": remote.get("size"),
        "sha256": sha256,
        "md5": md5,
        "dropbox_content_hash_local": dbx_hash,
        "dropbox_content_hash_remote": remote.get("content_hash"),
        "server_modified": remote.get("server_modified"),
        "rev": remote.get("rev"),
        "id": remote.get("id"),
    }
    rec["dropbox_hash_match"] = (
        "yes" if (dbx_hash and remote.get("content_hash") == dbx_hash) else ("no" if dbx_hash else "n/a")
    )
    return rec
