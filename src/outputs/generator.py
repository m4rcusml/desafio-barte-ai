"""
Emissor Atômico das Saídas Oficiais e Prova Real do Rastro (Camada Gold).
Gera simultaneamente em 'fechamento-completo/' e no diretório oficial 'saida/'.
"""

from __future__ import annotations
import csv
import shutil
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any

from ..engines.checkout_engine import ResultadoCheckout
from ..engines.cambio_engine import ResultadoRemessas
from ..engines.banking_engine import ResultadoContabil


def emitir_todos_os_entregaveis(
    res_checkout: ResultadoCheckout,
    res_remessas: ResultadoRemessas,
    res_contabil: ResultadoContabil,
    output_dir_local: Path,
    output_dir_oficial: Path,
) -> Dict[str, Any]:
    output_dir_local.mkdir(parents=True, exist_ok=True)
    output_dir_oficial.mkdir(parents=True, exist_ok=True)

    rastro_completo: List[Dict[str, str]] = []

    # 1. comissoes_por_lojista.csv
    comissoes_rows: List[Dict[str, str]] = []
    idx_com = 1
    map_com_checkout_id: Dict[str, str] = {}
    map_com_remessa_id: Dict[str, str] = {}

    for c in res_checkout.comissoes:
        id_saida = f"COM-{idx_com:04d}"
        idx_com += 1
        map_com_checkout_id[c.cnpj] = id_saida
        comissoes_rows.append({
            "id_saida": id_saida,
            "cnpj": c.cnpj,
            "lojista": c.lojista,
            "linha_negocio": "CHECKOUT",
            "comissao_brl": f"{c.comissao_brl:.2f}",
        })

    for c in res_remessas.comissoes:
        id_saida = f"COM-{idx_com:04d}"
        idx_com += 1
        map_com_remessa_id[c.cnpj] = id_saida
        comissoes_rows.append({
            "id_saida": id_saida,
            "cnpj": c.cnpj,
            "lojista": c.lojista,
            "linha_negocio": "REMESSA",
            "comissao_brl": f"{c.comissao_brl:.2f}",
        })

    # 2. divergencias_taxa.csv
    divergencias_rows: List[Dict[str, str]] = []
    idx_div = 1
    for d in res_checkout.divergencias:
        id_saida = f"DIV-{idx_div:04d}"
        idx_div += 1
        divergencias_rows.append({
            "id_saida": id_saida,
            "cnpj": d.cnpj,
            "linha_negocio": "CHECKOUT",
            "ref_origem": d.ref_origem,
            "taxa_contratada_pct": f"{d.taxa_contratada_pct:.2f}",
            "taxa_aplicada_pct": f"{d.taxa_aplicada_pct:.2f}",
            "diferenca_brl": f"{d.diferenca_brl:.2f}",
        })

    for d in res_remessas.divergencias:
        id_saida = f"DIV-{idx_div:04d}"
        idx_div += 1
        divergencias_rows.append({
            "id_saida": id_saida,
            "cnpj": d.cnpj,
            "linha_negocio": "REMESSA",
            "ref_origem": d.ref_origem,
            "taxa_contratada_pct": f"{d.taxa_contratada_pct:.2f}",
            "taxa_aplicada_pct": f"{d.taxa_aplicada_pct:.2f}",
            "diferenca_brl": f"{d.diferenca_brl:.2f}",
        })

    # 3. notas_a_emitir.csv
    notas_rows: List[Dict[str, str]] = []
    idx_nf = 1
    map_nf_remessa_id: str = ""

    for c in res_checkout.comissoes:
        if c.comissao_brl > Decimal("0.00"):
            id_saida = f"NF-{idx_nf:04d}"
            idx_nf += 1
            notas_rows.append({
                "id_saida": id_saida,
                "tomador_cnpj": c.cnpj,
                "tomador": c.lojista,
                "linha_negocio": "CHECKOUT",
                "valor_brl": f"{c.comissao_brl:.2f}",
                "discriminacao": f"Serviços de intermediação e facilitação de transações comerciais (Checkout) - Competência 09/2026. Lojista: {c.lojista}.",
            })

    if res_remessas.nota_ponte and res_remessas.nota_ponte.valor_brl > Decimal("0.00"):
        id_saida = f"NF-{idx_nf:04d}"
        idx_nf += 1
        map_nf_remessa_id = id_saida
        notas_rows.append({
            "id_saida": id_saida,
            "tomador_cnpj": res_remessas.nota_ponte.tomador_cnpj,
            "tomador": res_remessas.nota_ponte.tomador,
            "linha_negocio": "REMESSA",
            "valor_brl": f"{res_remessas.nota_ponte.valor_brl:.2f}",
            "discriminacao": res_remessas.nota_ponte.discriminacao,
        })

    # 4. lancamentos_classificados.csv
    lancamentos_rows: List[Dict[str, str]] = []
    idx_lan = 1
    for l in res_contabil.lancamentos:
        id_saida = f"LAN-{idx_lan:04d}"
        idx_lan += 1
        lancamentos_rows.append({
            "id_saida": id_saida,
            "banco": l.banco,
            "ref_origem": l.ref_origem,
            "data": l.data,
            "descricao": l.descricao,
            "valor": f"{l.valor:.2f}",
            "conta_codigo": l.conta_codigo,
            "metodo": l.metodo,
            "confianca": f"{l.confianca:.2f}",
        })

    # 5. pendencias.csv
    pendencias_rows: List[Dict[str, str]] = []
    idx_pen = 1
    for p in res_checkout.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        pendencias_rows.append({
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        })

    for p in res_remessas.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        pendencias_rows.append({
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        })

    for p in res_contabil.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        pendencias_rows.append({
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        })

    # 6. rastro.csv
    for r in res_checkout.rastro:
        id_com = map_com_checkout_id.get(r.id_saida, r.id_saida)
        rastro_completo.append({
            "id_saida": id_com,
            "arquivo_origem": r.arquivo_origem,
            "ref_origem": r.ref_origem,
            "valor": f"{r.valor:.2f}",
        })

    for r in res_remessas.rastro:
        id_com = map_com_remessa_id.get(r.id_saida, r.id_saida)
        rastro_completo.append({
            "id_saida": id_com,
            "arquivo_origem": r.arquivo_origem,
            "ref_origem": r.ref_origem,
            "valor": f"{r.valor:.2f}",
        })

    if map_nf_remessa_id:
        for r in res_remessas.rastro:
            rastro_completo.append({
                "id_saida": map_nf_remessa_id,
                "arquivo_origem": r.arquivo_origem,
                "ref_origem": r.ref_origem,
                "valor": f"{r.valor:.2f}",
            })

    # Salva em ambos os destinos
    outputs_map = {
        "comissoes_por_lojista.csv": (comissoes_rows, ["id_saida", "cnpj", "lojista", "linha_negocio", "comissao_brl"]),
        "divergencias_taxa.csv": (divergencias_rows, ["id_saida", "cnpj", "linha_negocio", "ref_origem", "taxa_contratada_pct", "taxa_aplicada_pct", "diferenca_brl"]),
        "notas_a_emitir.csv": (notas_rows, ["id_saida", "tomador_cnpj", "tomador", "linha_negocio", "valor_brl", "discriminacao"]),
        "lancamentos_classificados.csv": (lancamentos_rows, ["id_saida", "banco", "ref_origem", "data", "descricao", "valor", "conta_codigo", "metodo", "confianca"]),
        "pendencias.csv": (pendencias_rows, ["id_saida", "tipo", "ref_origem", "valor_brl", "motivo", "quem_decide"]),
        "rastro.csv": (rastro_completo, ["id_saida", "arquivo_origem", "ref_origem", "valor"]),
    }

    for fname, (rows, header) in outputs_map.items():
        for dest_dir in (output_dir_local, output_dir_oficial):
            fpath = dest_dir / fname
            with open(fpath, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)

    return {
        "comissoes_count": len(comissoes_rows),
        "divergencias_count": len(divergencias_rows),
        "notas_count": len(notas_rows),
        "lancamentos_count": len(lancamentos_rows),
        "pendencias_count": len(pendencias_rows),
        "rastro_count": len(rastro_completo),
    }
