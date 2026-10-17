"""
Formatador para 04_plano_de_contas_fenix_erp.csv
"""

from __future__ import annotations
import csv
from pathlib import Path
from ..utils import fmt_date_iso


def format_fenix_file(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tipo_map = {"SINTETICA": 1, "ANALITICA": 2}

    rows_processed = 0
    with open(input_path, mode="r", encoding="cp1252", errors="ignore") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        fieldnames = reader.fieldnames or []

        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()

            for row in reader:
                tipo_raw = row.get("TIPO", "").strip()
                tipo_cod = tipo_map.get(tipo_raw.upper(), tipo_raw)
                desc_raw = row.get("DESCRICAO", "").strip()
                if desc_raw.upper() in tipo_map:
                    desc_raw = str(tipo_map[desc_raw.upper()])

                formatted_row = {
                    "COD_CONTA": row.get("COD_CONTA", "").strip(),
                    "DESCRICAO": desc_raw,
                    "TIPO": str(tipo_cod),
                    "NATUREZA": row.get("NATUREZA", "").strip(),
                    "ACEITA_LANCTO": row.get("ACEITA_LANCTO", "").strip(),
                    "COD_SUPERIOR": row.get("COD_SUPERIOR", "").strip(),
                    "DT_CRIACAO": fmt_date_iso(row.get("DT_CRIACAO")),
                }
                writer.writerow(formatted_row)
                rows_processed += 1

    return rows_processed
