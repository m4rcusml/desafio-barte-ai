"""
Formatador para 05a_extrato_banco_aurora_cc4471_set2026.csv
"""

from __future__ import annotations
import csv
import re
from pathlib import Path
from typing import Tuple

from ..utils import fmt_date_iso, fmt_money_br_to_dot


def extract_aurora_metadata(header_lines: list[str]) -> Tuple[str, str, str, str, str, str]:
    line0 = header_lines[0].split(";")[0].strip()
    banco = re.sub(r"[^A-Z0-9]", "", line0.upper())

    line2 = header_lines[2] if len(header_lines) > 2 else ""
    m_cli = re.search(r"Cliente:\s*([^;]+)", line2, re.IGNORECASE)
    cliente = re.sub(r"[^A-Z0-9]", "", m_cli.group(1).upper()) if m_cli else ""

    m_cnpj = re.search(r"CNPJ:\s*([^;]+)", line2, re.IGNORECASE)
    cnpj = re.sub(r"\D", "", m_cnpj.group(1)) if m_cnpj else ""

    line3 = header_lines[3] if len(header_lines) > 3 else ""
    m_ag = re.search(r"Agência:\s*([^;]+)", line3, re.IGNORECASE)
    agencia = re.sub(r"[^A-Z0-9]", "", m_ag.group(1)) if m_ag else ""

    m_cc = re.search(r"Conta:\s*([^;]+)", line3, re.IGNORECASE)
    conta = re.sub(r"[^A-Z0-9]", "", m_cc.group(1)) if m_cc else ""

    line4 = header_lines[4] if len(header_lines) > 4 else ""
    m_per = re.search(r"(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})", line4)
    if m_per:
        d1, m1, y1 = m_per.group(1).split("/")
        d2, m2, y2 = m_per.group(2).split("/")
        periodo = f"{y1}-{m1}-{d1}_{y2}-{m2}-{d2}"
    else:
        periodo = ""

    return banco, cliente, cnpj, agencia, conta, periodo


def format_aurora_file(input_path: Path, output_dir: Path) -> Tuple[Path, int]:
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path, mode="r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_lines = lines[:10]
    banco, cliente, cnpj, agencia, conta, periodo = extract_aurora_metadata(header_lines)
    target_filename = f"{banco}-EXTRATODECONTACORRENTE-{cliente}-{cnpj}-{agencia}-{conta}-{periodo}.csv"
    output_path = output_dir / target_filename

    data_start_idx = -1
    for idx, l in enumerate(lines):
        if l.strip().startswith("Data;"):
            data_start_idx = idx
            break

    if data_start_idx == -1:
        raise ValueError("Linha de cabeçalho das transações do Banco Aurora não encontrada.")

    reader = csv.DictReader(lines[data_start_idx:], delimiter=";")
    fieldnames = ["data", "lancamento", "documento", "valor", "saldo"]

    rows_processed = 0
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for row in reader:
            dt = row.get("Data", "").strip()
            if not dt or dt.lower().startswith("saldo") or dt.lower().startswith("total"):
                continue

            writer.writerow({
                "data": fmt_date_iso(dt),
                "lancamento": row.get("Histórico", "").strip(),
                "documento": row.get("Documento", "").strip(),
                "valor": fmt_money_br_to_dot(row.get("Valor (R$)", "")),
                "saldo": fmt_money_br_to_dot(row.get("Saldo (R$)", "")),
            })
            rows_processed += 1

    return output_path, rows_processed
