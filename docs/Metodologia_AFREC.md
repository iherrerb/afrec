# Metodología AFREC (basada en NIST SP 800-86 e ISO/IEC 27037:2012)

**Fase 1 – Preparación:** autorización formal, entorno controlado, obtención/registro de token OAuth2.  
**Fase 2 – Conexión Segura a la API:** sesión cifrada, validación de token, registro de contexto (UTC, IP, identificador).  
**Fase 3 – Identificación de Evidencias:** `files/list_folder` recursivo, metadatos completos, inventario JSON/CSV.  
**Fase 4 – Adquisición de Evidencias:** `files/download`, descarga controlada con reintentos, verificación de rate limits.  
**Fase 5 – Preservación y Documentación:** consolidación de logs, hashes, cadena de custodia; reporte PDF.  
**Fase 6 – Validación del Procedimiento:** comparación de hashes e inventario, pruebas de reproducibilidad y escenarios adversos.

## Consideraciones Éticas y Legales
Uso exclusivo con autorización; cumplimiento de RGPD / Ley 1581/2012; protección de tokens, evidencias y logs.
