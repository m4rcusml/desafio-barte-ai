"""
Formatador de Arquivos Orbe (01 Principal e 06 Ajustes Tardios).
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict

from ..utils import LEGENDS, fmt_date_iso, fmt_decimal_dot


def format_orbe_file(input_path: Path, output_path: Path) -> int:
    tipo_map: Dict[str, int] = LEGENDS.get("orbe_tipo_lancamento", {})
    mod_map: Dict[str, int] = LEGENDS.get("orbe_modalidade", {})
    bandeira_map: Dict[str, int] = LEGENDS.get("orbe_bandeira", {})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows_processed = 0

    with open(input_path, mode="r", encoding="utf-8", errors="ignore") as infile:
        reader = csv.DictReader(infile, delimiter=";")
        fieldnames = reader.fieldnames or []
        obrigatorias = {"id_transacao", "data_movimento", "cod_estabelecimento", "valor_bruto"}
        if not obrigatorias.issubset(set(fieldnames)):
            raise ValueError(
                f"Layout inválido no arquivo Orbe '{input_path.name}': colunas obrigatórias {sorted(obrigatorias)} ausentes em {fieldnames}."
            )

        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()

            for row in reader:
                tipo_str = row.get("tipo_lancamento", "").strip()
                mod_str = row.get("modalidade", "").strip()
                band_str = row.get("bandeira", "").strip()

                formatted_row = {
                    "id_transacao": row.get("id_transacao", "").strip(),
                    "data_movimento": fmt_date_iso(row.get("data_movimento")),
                    "cod_estabelecimento": row.get("cod_estabelecimento", "").strip(),
                    "nome_estabelecimento": row.get("nome_estabelecimento", "").strip(),
                    "tipo_lancamento": str(tipo_map.get(tipo_str, 0)),
                    "modalidade": str(mod_map.get(mod_str, 0)),
                    "qtd_parcelas": row.get("qtd_parcelas", "").strip(),
                    "bandeira": str(bandeira_map.get(band_str, 0)),
                    "valor_bruto": fmt_decimal_dot(row.get("valor_bruto")),
                    "taxa_aplicada_pct": fmt_decimal_dot(row.get("taxa_aplicada_pct")),
                    "valor_taxa": fmt_decimal_dot(row.get("valor_taxa")),
                    "valor_liquido": fmt_decimal_dot(row.get("valor_liquido")),
                    "id_referencia": row.get("id_referencia", "").strip(),
                    "data_venda_original": fmt_date_iso(row.get("data_venda_original")),
                }
                writer.writerow(formatted_row)
                rows_processed += 1

    return rows_processed
