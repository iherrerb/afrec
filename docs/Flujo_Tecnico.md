# Flujo Técnico

1. `afrec auth`: flujo OAuth2, guarda token cifrado en `secrets/token.enc`.
2. `afrec preview`: genera inventario lógico (JSON/CSV) con filtros por extensión y rango de fechas.
3. `afrec acquire`: descarga secuencial, calcula hashes (SHA-256/MD5 y Dropbox Content Hash local), guarda CSV/JSON y PDF, y actualiza cadena de custodia.
4. Análisis posterior: verificación y validación con los artefactos en la carpeta del caso.
