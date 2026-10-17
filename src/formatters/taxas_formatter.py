"""
Formatador para 02_tabela_taxas_contratadas.xlsx
"""

from __future__ import annotations
import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict

from ..utils import fmt_clean_cnpj, fmt_vigencia, fmt_decimal_dot


def _read_sheet_cells(z: zipfile.ZipFile, sheet_filename: str) -> List[Dict[str, str]]:
    s_xml = ET.fromstring(z.read(sheet_filename))
    rows = s_xml.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row")
    result = []
    for r in rows:
        row_dict: Dict[str, str] = {}
        for c in r.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
            ref = c.attrib.get("r", "")
            col = "".join(ch for ch in ref if ch.isalpha())
            v = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
            is_tag = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is")
            val = ""
            if v is not None and v.text:
                val = v.text
            elif is_tag is not None:
                val = "".join(is_tag.itertext())
            row_dict[col] = val
        result.append(row_dict)
    return result


def format_taxas_file(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_path) as z:
        sheet_rows = _read_sheet_cells(z, "xl/worksheets/sheet1.xml")

    header_idx = -1
    for idx, r in enumerate(sheet_rows):
        if r.get("A", "").strip().lower() == "lojista":
            header_idx = idx
            break

    if header_idx == -1:
        raise ValueError("Cabeçalho da tabela de taxas não encontrado na planilha.")

    fieldnames = [
        "lojista", "cnpj", "ec_orbe", "debito", "credito_a_vista",
        "cred_2_6x", "cred_7_12x", "pix", "antecipacao", "spread_remessa",
        "vigencia", "obs"
    ]

    rows_processed = 0
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for r in sheet_rows[header_idx + 1:]:
            lojista = r.get("A", "").strip()
            if not lojista or lojista.startswith("*"):
                continue

            raw_cnpj = r.get("B", "")
            clean_cnpj = fmt_clean_cnpj(raw_cnpj)

            row_data = {
                "lojista": lojista,
                "cnpj": clean_cnpj,
                "ec_orbe": r.get("C", "").strip(),
                "debito": fmt_decimal_dot(r.get("D", "")),
                "credito_a_vista": fmt_decimal_dot(r.get("E", "")),
                "cred_2_6x": fmt_decimal_dot(r.get("F", "")),
                "cred_7_12x": fmt_decimal_dot(r.get("G", "")),
                "pix": fmt_decimal_dot(r.get("H", "")),
                "antecipacao": fmt_decimal_dot(r.get("I", "")),
                "spread_remessa": fmt_decimal_dot(r.get("J", "")),
                "vigencia": fmt_vigencia(r.get("K", "")),
                "obs": r.get("L", "").strip(),
            }
            writer.writerow(row_data)
            rows_processed += 1

    return rows_processed
