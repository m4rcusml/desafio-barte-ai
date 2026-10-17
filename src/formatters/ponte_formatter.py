"""
Formatador para 03_email_ponte_cambio_relatorio_set2026.eml
"""

from __future__ import annotations
import csv
import io
import email
from email import policy
from datetime import datetime, timedelta
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict

from ..utils import fmt_clean_cnpj, fmt_decimal_dot


def _excel_serial_to_date(serial_str: str) -> str:
    if not serial_str:
        return ""
    try:
        serial_int = int(float(serial_str))
        base = datetime(1899, 12, 30)
        dt = base + timedelta(days=serial_int)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return serial_str


def _read_sheet_cells_from_bytes(data: bytes, sheet_name: str = "xl/worksheets/sheet1.xml") -> List[Dict[str, str]]:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        s_xml = ET.fromstring(z.read(sheet_name))
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


def format_ponte_file(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    excel_bytes = None
    for part in msg.walk():
        fn = part.get_filename()
        if fn and fn.endswith(".xlsx"):
            excel_bytes = part.get_payload(decode=True)
            break

    if not excel_bytes:
        raise ValueError("Anexo .xlsx não encontrado no e-mail da Ponte Câmbio.")

    sheet_rows = _read_sheet_cells_from_bytes(excel_bytes, "xl/worksheets/sheet1.xml")

    header_idx = -1
    for idx, r in enumerate(sheet_rows):
        if "operação" in r.get("A", "").lower() or "operacao" in r.get("A", "").lower():
            header_idx = idx
            break

    if header_idx == -1:
        raise ValueError("Cabeçalho não encontrado na aba Operações da Ponte Câmbio.")

    fieldnames = [
        "num_operacao", "data_contratacao", "data_liquidacao", "cnpj_cliente",
        "cliente", "moeda", "valor_me", "taxa_cliente", "ptax_ref",
        "valor_brl", "spread_brl", "spread_pct", "spread_estimado_brl",
        "iof_brl", "status_compliance", "observacao", "arquivo_origem"
    ]

    rows_processed = 0
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for r in sheet_rows[header_idx + 1:]:
            op_num = r.get("A", "").strip()
            if not op_num or op_num.startswith("Total") or op_num.startswith("Spread"):
                continue

            raw_cnpj = r.get("D", "")
            clean_cnpj = fmt_clean_cnpj(raw_cnpj)

            row_data = {
                "arquivo_origem": input_path.name,
                "num_operacao": op_num,
                "data_contratacao": _excel_serial_to_date(r.get("B", "")),
                "data_liquidacao": _excel_serial_to_date(r.get("C", "")),
                "cnpj_cliente": clean_cnpj,
                "cliente": r.get("E", "").strip(),
                "moeda": r.get("F", "").strip(),
                "valor_me": fmt_decimal_dot(r.get("G", "")),
                "taxa_cliente": fmt_decimal_dot(r.get("H", "")),
                "ptax_ref": fmt_decimal_dot(r.get("I", "")),
                "valor_brl": fmt_decimal_dot(r.get("J", "")),
                "spread_brl": fmt_decimal_dot(r.get("K", "")),
                "spread_pct": fmt_decimal_dot(r.get("L", "")),
                "spread_estimado_brl": fmt_decimal_dot(r.get("M", "")),
                "iof_brl": fmt_decimal_dot(r.get("N", "")),
                "status_compliance": r.get("O", "").strip(),
                "observacao": r.get("P", "").strip(),
            }
            writer.writerow(row_data)
            rows_processed += 1

    return rows_processed
