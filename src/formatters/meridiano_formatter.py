"""
Formatador para 05b_extrato_banco_meridiano_cc90233_set2026.ofx
"""

from __future__ import annotations
import csv
import re
from pathlib import Path
from typing import Tuple

from ..utils import fmt_date_iso, fmt_decimal_dot


def format_meridiano_file(input_path: Path, output_dir: Path) -> Tuple[Path, int]:
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="latin1", errors="ignore") as f:
        ofx_text = f.read()

    if "<OFX>" not in ofx_text.upper() and "<STMTRS>" not in ofx_text.upper():
        raise ValueError(f"Layout OFX inválido ou corrompido no arquivo '{input_path.name}'.")

    m_branch = re.search(r"<BRANCHID>(\d+)", ofx_text)
    m_acct = re.search(r"<ACCTID>([^<\r\n]+)", ofx_text)
    m_dtstart = re.search(r"<DTSTART>(\d{8})", ofx_text)
    m_dtend = re.search(r"<DTEND>(\d{8})", ofx_text)

    branch_str = m_branch.group(1).strip() if m_branch else "0091"
    acct_str = re.sub(r"[^A-Z0-9]", "", m_acct.group(1).upper()) if m_acct else "902335"

    d1_str = fmt_date_iso(m_dtstart.group(1)) if m_dtstart else "2026-09-01"
    d2_str = fmt_date_iso(m_dtend.group(1)) if m_dtend else "2026-09-30"
    periodo_str = f"{d1_str}_{d2_str}"

    target_filename = f"BANCOMERIDIANO-EXTRATODECONTACORRENTE-TARVOPAGAMENTOSLTDA-84626315000139-{branch_str}-{acct_str}-{periodo_str}.csv"
    output_path = output_dir / target_filename

    trns = re.findall(r"<STMTTRN>(.*?)</STMTTRN>", ofx_text, re.DOTALL)
    fieldnames = ["data", "fitid", "tipo", "documento", "lancamento", "valor", "arquivo_origem"]

    rows_processed = 0
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for t in trns:
            m_type = re.search(r"<TRNTYPE>([^<\r\n]+)", t)
            m_dt = re.search(r"<DTPOSTED>(\d{8})", t)
            m_amt = re.search(r"<TRNAMT>([^<\r\n]+)", t)
            m_fitid = re.search(r"<FITID>([^<\r\n]+)", t)
            m_chk = re.search(r"<CHECKNUM>([^<\r\n]+)", t)
            m_memo = re.search(r"<MEMO>([^<\r\n]+)", t)

            writer.writerow({
                "data": fmt_date_iso(m_dt.group(1)) if m_dt else "",
                "fitid": m_fitid.group(1).strip() if m_fitid else "",
                "arquivo_origem": input_path.name,
                "tipo": m_type.group(1).strip() if m_type else "",
                "documento": m_chk.group(1).strip() if m_chk else "",
                "lancamento": m_memo.group(1).strip() if m_memo else "",
                "valor": fmt_decimal_dot(m_amt.group(1)) if m_amt else "0.00",
            })
            rows_processed += 1

    return output_path, rows_processed
