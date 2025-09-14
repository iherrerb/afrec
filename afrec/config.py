""" Aquí se Maneja la configuración global del proyecto.
Carga variables desde .env (ejemplo: DROPBOX_APP_KEY, DROPBOX_APP_SECRET).
Define rutas estándar (cases/, logs/, secrets/).
Garantiza consistencia y centralización de parámetros. """

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    # Archivos del sistema
    repo_root: Path
    cases_dir: Path
    logs_dir: Path
    secrets_dir: Path
    # Credenciales de Dropbox (OAuth2)
    dropbox_app_key: Optional[str] = None
    dropbox_app_secret: Optional[str] = None
    
    timezone: str = "UTC"

    @staticmethod
    def load() -> "Settings":
        root = Path(os.getenv("AFREC_ROOT", Path.cwd()))
        cases = Path(os.getenv("AFREC_CASES_DIR", root / "cases"))
        logs = Path(os.getenv("AFREC_LOGS_DIR", root / "logs"))
        secrets = Path(os.getenv("AFREC_SECRETS_DIR", root / "secrets"))
        app_key = os.getenv("DROPBOX_APP_KEY")
        app_secret = os.getenv("DROPBOX_APP_SECRET")
        return Settings(
            repo_root=root,
            cases_dir=cases,
            logs_dir=logs,
            secrets_dir=secrets,
            dropbox_app_key=app_key,
            dropbox_app_secret=app_secret,
            timezone=os.getenv("AFREC_TZ", "UTC"),
        )
