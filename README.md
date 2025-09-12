# AFREC — Adquisición Forense de Recursos en la Nube (Dropbox)

Herramienta de línea de comandos para **obtener y preservar evidencia digital** en entornos de almacenamiento en la nube (Dropbox) cumpliendo principios de **autenticidad, integridad, reproducibilidad y cadena de custodia**.

> **Uso autorizado únicamente.** Requiere orden judicial, consentimiento o autorización contractual. Proteja los tokens y la información sensible en todo momento.

---

## Arquitectura del proyecto

```
afrec/
├── afrec/                 # Paquete principal
│   ├── cli.py             # CLI Typer: auth, preview, acquire
│   ├── explorer.py        # Inventario lógico (list_folder)
│   ├── downloader.py      # Descarga controlada + reintentos
│   ├── integrity.py       # Hashes SHA-256, MD5, Dropbox Content Hash
│   ├── reports.py         # CSV / JSON / PDF resumen forense
│   ├── custody.py         # Cadena de custodia JSONL
│   ├── session.py         # Sesión (actor, IP, fecha)
│   ├── logging_utils.py   # Logging JSON (archivo y consola)
│   ├── crypto.py          # Token cifrado (Fernet + PBKDF2)
│   └── config.py          # Carga de variables de entorno y rutas
├── cases/                 # Casos generados por la herramienta
├── secrets/               # Almacenamiento de token cifrado (token.enc)
├── tests/                 # Pruebas unitarias (pytest)
├── docs/                  # Metodología y guía
├── .github/workflows/ci.yml
├── .vscode/               # Configuración recomendada para VS Code
├── pyproject.toml         # Metadatos, dependencias y tooling
├── requirements.txt       # Alternativa para `pip install -r`
└── README.md
```

## Requisitos

- Python 3.8+
- Cuenta de desarrollador en Dropbox y **App** con permisos `files.metadata.read` y `files.content.read`.
- Visual Studio Code (recomendado).

Instalación de dependencias:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
# o: pip install -r requirements.txt
```

Cree un archivo `.env` en la raíz con:

```
DROPBOX_APP_KEY=su_app_key
DROPBOX_APP_SECRET=su_app_secret
AFREC_TZ=UTC
```

## Uso rápido (CLI)

1) **Autenticación y almacenamiento seguro del token**

```bash
afrec auth
# Abre URL, autoriza y pegue el código. Se guarda secrets/token.enc (cifrado).
```

2) **Vista previa (inventario lógico)**

```bash
afrec preview --path "/carpeta_de_documentos" --ext ".pdf,.docx" --date-from "2025-01-01"
```

3) **Adquisición (descarga + hashes + reporte + custodia)**

```bash
afrec acquire --path "/carpeta_de_documentos" --ext ".pdf,.docx" --date-from "2025-01-01"
```

Esto crea una carpeta en `cases/AAAA-MM-DD_UUID/` con:
- `session.json`, `log.txt`
- `inventario.json`, `inventario.csv`
- `evidence/` (estructura de carpetas preservada)
- `hashes.csv`
- `cadena_custodia.jsonl`
- `reporte.pdf`

## Estándares y buenas prácticas

- **Trazabilidad:** logs en formato JSON y cadena de custodia JSONL por cada acción.
- **Integridad:** doble verificación de hash (local SHA-256/MD5 + Dropbox Content Hash si disponible).
- **Reproducibilidad:** procesos deterministas y descarga secuencial.
- **Seguridad:** token cifrado con passphrase (PBKDF2 + Fernet).
- **Calidad:** `ruff`, `black`, `mypy`, `pytest` y CI en GitHub Actions.
- **Documentación:** metodología en `docs/` y README con pasos claros.

## Desarrollo con VS Code

- Extensiones recomendadas: Python, Pylance.
- Formateo automático: Black.
- Tareas y depuración en `.vscode/`.

## Licencia

MIT. Véase `LICENSE`.
