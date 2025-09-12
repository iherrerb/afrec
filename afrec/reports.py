from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def write_csv(records: Iterable[Dict[str, Any]], path: Path, headers: List[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    recs = list(records)
    if not headers and recs:
        headers = list(recs[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for r in recs:
            writer.writerow(r)


def generate_pdf_report(
    out_file: Path,
    summary: Dict[str, Any],
    session: Dict[str, Any],
) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Configuración del documento con márgenes estándar
    doc = SimpleDocTemplate(
        str(out_file),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Encabezado
    logo_path = "C:/Users/ivan_/OneDrive - Consejo Superior de la Judicatura/Documentos/PERSONALES\MAESTRÍA_SEGURIDAD_TIC\M10_TFM/proyecto_afrec/afrec/logo.png"  # ajusta la ruta a tu archivo
    logo = Image(logo_path, width=6*cm, height=2*cm)  # tamaño del logo
    logo.hAlign = "LEFT"  # alinear a la izquierda
    story.append(logo)
    story.append(Spacer(1, 12))  # espacio debajo del logo

    story.append(Paragraph("<b>AFREC – Reporte de Adquisición Forense (Dropbox)</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Fecha de generación (UTC): {datetime.now(timezone.utc).isoformat()}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Datos de la sesión
    story.append(Paragraph("<b>Datos de la Sesión</b>", styles['Heading2']))
    data_session = [
        ["ID de sesión", session.get("id")],
        ["Actor", session.get("actor")],
        ["Dirección IP", session.get("ip_address")],
        ["Fecha de inicio (UTC)", session.get("started_at")],
    ]
    table1 = Table(data_session, colWidths=[6*cm, 8*cm])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(table1)
    story.append(Spacer(1, 20))

    # Resumen de adquisición
    story.append(Paragraph("<b>Resumen de la Adquisición</b>", styles['Heading2']))
    #data_summary = [[str(k), str(v)] for k, v in summary.items()]
    data_summary = []
    for k, v in summary.items():
        val = Paragraph(str(v), styles['Normal'])  # wrap automático
        data_summary.append([k, val])

    table2 = Table(data_summary, colWidths=[6*cm, 8*cm])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    story.append(table2)

    # Construir el PDF
    doc.build(story)