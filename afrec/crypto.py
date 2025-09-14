""" Gestiona el cifrado seguro de tokens OAuth2.
Usa cryptography.Fernet con clave derivada de una passphrase (PBKDF2 + SHA-256).
Archivos cifrados se guardan como secrets/token.enc.
Funciones principales:
TokenStore.save() → guarda token cifrado.
TokenStore.load() → descifra token cuando se usa. 
Protege credenciales sensibles de Dropbox"""

from __future__ import annotations

import base64
import getpass
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


@dataclass
class TokenBundle:
    access_token: str
    refresh_token: str | None = None
    expires_at: str | None = None  # formato de tiempo estándar ISO8601

    def fingerprint(self) -> str:
        import hashlib
        src = (self.refresh_token or self.access_token).encode("utf-8")
        return hashlib.sha256(src).hexdigest()[:16]


class TokenStore:
    def __init__(self, file: Path) -> None:
        self.file = file

    def save(self, bundle: TokenBundle, passphrase: Optional[str] = None) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        salt = os.urandom(16)
        if passphrase is None:
            passphrase = getpass.getpass("Passphrase to encrypt tokens: ")
        key = _derive_key(passphrase, salt)
        f = Fernet(key)
        payload = json.dumps(bundle.__dict__, ensure_ascii=False).encode("utf-8")
        token = f.encrypt(payload)
        with open(self.file, "wb") as fh:
            fh.write(b"AFREC1\n")
            fh.write(base64.b64encode(salt) + b"\n")
            fh.write(token)

    def load(self, passphrase: Optional[str] = None) -> TokenBundle:
        if passphrase is None:
            passphrase = getpass.getpass("Passphrase to decrypt tokens: ")
        with open(self.file, "rb") as fh:
            header = fh.readline().strip()
            if header != b"AFREC1":
                raise ValueError("Invalid token file header")
            salt_b64 = fh.readline().strip()
            salt = base64.b64decode(salt_b64)
            blob = fh.read()
        key = _derive_key(passphrase, salt)
        f = Fernet(key)
        raw = f.decrypt(blob)
        data = json.loads(raw.decode("utf-8"))
        return TokenBundle(**data)
