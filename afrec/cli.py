""" Esta es la interfaz de línea de comandos (CLI) de AFREC.
Usa Typer y Rich para crear comandos con buena experiencia en consola.
Contiene los comandos principales:
* afrec auth → flujo OAuth2 y guardado del token.
* afrec preview → genera inventario lógico (JSON/CSV).
* afrec acquire → adquiere evidencias, genera hashes, reportes y cadena de custodia.
Se conecta con el resto de módulos (explorer, downloader, reports, custody). 
Es el punto de entreda para los usuarios"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, List

import typer
from rich import print
from rich.table import Table

from dropbox import Dropbox, DropboxOAuth2FlowNoRedirect
from dropbox.exceptions import AuthError

from .config import Settings
from .custody import ChainOfCustody, CustodyEntry
from .explorer import InventoryItem, list_inventory, save_inventory_csv, save_inventory_json
from .downloader import download_files
from .logging_utils import setup_logging
from .reports import generate_pdf_report, write_csv
from .session import Session
from .utils import utc_now_iso
from .crypto import TokenStore, TokenBundle

app = typer.Typer(help="AFREC - Adquisición Forense de Recursos en la Nube (Dropbox)")


@app.command()
def auth(
    passphrase: Optional[str] = typer.Option(None, help="Passphrase para cifrar el token en disco"),
    app_key: Optional[str] = typer.Option(None, help="DROPBOX_APP_KEY (si no está en .env)"),
    app_secret: Optional[str] = typer.Option(None, help="DROPBOX_APP_SECRET (si no está en .env)"),
):
    """Realiza el flujo OAuth2 (No-Redirect) y guarda el token cifrado en ./secrets/token.enc"""
    settings = Settings.load()
    app_key = app_key or settings.dropbox_app_key
    app_secret = app_secret or settings.dropbox_app_secret
    if not app_key or not app_secret:
        raise typer.BadParameter("Faltan credenciales DROPBOX_APP_KEY / DROPBOX_APP_SECRET")
    flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret, token_access_type="offline")
    authorize_url = flow.start()
    print("[bold]1)[/bold] Abra la siguiente URL, autorice la app y copie el código de autorización:")
    print(authorize_url)
    code = typer.prompt("Código de autorización")
    oauth_result = flow.finish(code)
    # Guardar tokens cifrados
    store = TokenStore(settings.secrets_dir / "token.enc")
    bundle = TokenBundle(
        access_token=oauth_result.access_token,
        refresh_token=getattr(oauth_result, "refresh_token", None),
        expires_at=None,
    )
    store.save(bundle, passphrase)
    print(f"Token guardado en {store.file}")


@app.command()
def preview(
    path: str = typer.Option("/", help="Carpeta raíz de Dropbox a analizar"),
    ext: Optional[str] = typer.Option(None, help="Extensiones separadas por coma, p.ej. .pdf,.docx"),
    date_from: Optional[str] = typer.Option(None, help="Fecha desde (YYYY-MM-DD o ISO8601)"),
    date_to: Optional[str] = typer.Option(None, help="Fecha hasta (YYYY-MM-DD o ISO8601)"),
    save: bool = typer.Option(True, help="Guardar inventario en casos/SESSION/inventario.(json|csv)"),
):
    """Muestra y (opcionalmente) guarda el inventario lógico de la carpeta especificada."""
    settings = Settings.load()
    client, actor, fingerprint = ensure_client(settings)

    session = Session.start(actor=actor)
    case_dir = settings.cases_dir / f"{session.started_at[:10]}_{session.id[:8]}"
    inventory_json = case_dir / "inventario.json"
    inventory_csv = case_dir / "inventario.csv"
    log_file = case_dir / "log.txt"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = setup_logging(log_file)
    logger.info(
    "start_preview",
    extra={
        "session_id": session.id,
        "actor": actor,
        "ip": session.ip_address,
        "path": path,
    },
)


    exts = [e.strip() for e in ext.split(",")] if ext else None
    items = list_inventory(client, root=path, exts=exts, date_from=date_from, date_to=date_to)

    table = Table(title=f"Inventario de {path} ({len(items)} archivos)")
    table.add_column("path")
    table.add_column("size")
    table.add_column("server_modified")
    for i in items[:50]:
        table.add_row(i.path_display, str(i.size), i.server_modified)
    print(table)
    if len(items) > 50:
        print(f"... mostrando 50 de {len(items)} elementos")

    if save:
        session.save(case_dir / "session.json")
        save_inventory_json(items, inventory_json)
        save_inventory_csv(items, inventory_csv)
        ChainOfCustody(case_dir / "cadena_custodia.jsonl").append(
            CustodyEntry.create(actor=actor, action="PREVIEW", path=path, count=len(items))
        )
        print(f"Inventario guardado en: {inventory_json} y {inventory_csv}")
    logger.info(
    "end_preview",
    extra={"count": len(items), "session_id": session.id},
)



@app.command()
def acquire(
    path: str = typer.Option("/", help="Carpeta raíz de Dropbox a adquirir"),
    ext: Optional[str] = typer.Option(None, help="Extensiones separadas por coma, p.ej. .pdf,.docx"),
    date_from: Optional[str] = typer.Option(None, help="Fecha desde (YYYY-MM-DD o ISO8601)"),
    date_to: Optional[str] = typer.Option(None, help="Fecha hasta (YYYY-MM-DD o ISO8601)"),
):
    """Realiza la adquisición forense: descarga, hashes, reportes y cadena de custodia."""
    settings = Settings.load()
    client, actor, fingerprint = ensure_client(settings)

    session = Session.start(actor=actor)
    case_dir = settings.cases_dir / f"{session.started_at[:10]}_{session.id[:8]}"
    evidence_dir = case_dir / "evidence"
    hashes_csv = case_dir / "hashes.csv"
    log_file = case_dir / "log.txt"
    report_pdf = case_dir / "reporte.pdf"
    inventory_json = case_dir / "inventario.json"
    inventory_csv = case_dir / "inventario.csv"

    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = setup_logging(log_file)
    
    logger.info(
    "start_acquire",
    extra={
        "session_id": session.id,
        "actor": actor,
        "ip": session.ip_address,
        "path": path,
    },
    )
    exts = [e.strip() for e in ext.split(",")] if ext else None
    items = list_inventory(client, root=path, exts=exts, date_from=date_from, date_to=date_to)
   
    session.save(case_dir / "session.json")
    save_inventory_json(items, inventory_json)
    save_inventory_csv(items, inventory_csv)

    raw_items = [i.__dict__ for i in items]
    hash_records = download_files(client, raw_items, evidence_dir)
    write_csv(hash_records, hashes_csv)

    summary = {
        "archivos_en_inventario": len(items),
        "archivos_descargados": len(hash_records),
        "ruta_evidencia": str(evidence_dir),
        "hashes_csv": str(hashes_csv),
        "fingerprint_token": fingerprint,
        "fecha_utc": utc_now_iso(),
    }
    generate_pdf_report(report_pdf, summary, session.__dict__)

    ChainOfCustody(case_dir / "cadena_custodia.jsonl").append(
        CustodyEntry.create(
            actor=actor,
            action="ACQUIRE",
            path=path,
            count=len(hash_records),
            case_dir=str(case_dir),
        )
    )

    print(f"[bold green]Adquisición completada.[/bold green] Carpeta del caso: {case_dir}")
    print(f"  - Inventario: {inventory_json.name}, {inventory_csv.name}")
    print(f"  - Hashes: {hashes_csv.name}")
    print(f"  - Reporte: {report_pdf.name}")
    
    logger.info(
    "end_acquire",
    extra={"count": len(items), "session_id": session.id},)

def _build_client(bundle: TokenBundle, settings: Settings) -> Dropbox:
    if bundle.refresh_token:
        return Dropbox(
            app_key=settings.dropbox_app_key,
            app_secret=settings.dropbox_app_secret,
            oauth2_refresh_token=bundle.refresh_token,
        )
    return Dropbox(oauth2_access_token=bundle.access_token)


def ensure_client(settings: Settings) -> Tuple[Dropbox, str, str]:
    store = TokenStore(settings.secrets_dir / "token.enc")
    bundle = store.load()
    dbx = _build_client(bundle, settings)
    try:
        acct = dbx.users_get_current_account()
    except AuthError as e:  
        raise typer.BadParameter("Token inválido o expirado. Ejecute 'afrec auth' nuevamente.") from e
    actor = acct.name.display_name or "unknown"
    return dbx, actor, bundle.fingerprint()


if __name__ == "__main__":
    app()
