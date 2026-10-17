"""
Motor de Remessas e Câmbio (Camada Gold).
"""

from __future__ import annotations
import csv
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Set, Any

from ..utils import round_half_up


@dataclass
class LinhaComissaoRemessa:
    cnpj: str
    lojista: str
    linha_negocio: str  # 'REMESSA'
    comissao_brl: Decimal
    operacoes_count: int = 0
    id_saida: str = ""


@dataclass
class LinhaDivergenciaRemessa:
    cnpj: str
    linha_negocio: str
    ref_origem: str
    taxa_contratada_pct: Decimal
    taxa_aplicada_pct: Decimal
    diferenca_brl: Decimal
    id_saida: str = ""


@dataclass
class LinhaNotaRemessa:
    tomador_cnpj: str
    tomador: str
    linha_negocio: str
    valor_brl: Decimal
    discriminacao: str
    id_saida: str = ""


@dataclass
class LinhaPendenciaRemessa:
    tipo: str
    ref_origem: str
    valor_brl: Decimal
    motivo: str
    quem_decide: str
    id_saida: str = ""


@dataclass
class LinhaRastroRemessa:
    id_saida: str
    arquivo_origem: str
    ref_origem: str
    valor: Decimal
    regra_aplicada: str = ""
    taxa_contratada_aplicada: str = ""
    detalhe_calculo: str = ""


@dataclass
class ResultadoRemessas:
    comissoes: List[LinhaComissaoRemessa]
    divergencias: List[LinhaDivergenciaRemessa]
    nota_ponte: LinhaNotaRemessa
    pendencias: List[LinhaPendenciaRemessa]
    rastro: List[LinhaRastroRemessa]
    total_comissao_tarvo: Decimal = Decimal("0.00")


def processar_remessas(
    ponte_csv_path: Path,
    tabela_taxas_path: Path,
) -> ResultadoRemessas:
    # 1. Carrega taxas contratadas de remessa
    contratos_remessa: Dict[str, Dict[str, Any]] = {}
    with open(tabela_taxas_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            cnpj = row.get("cnpj", "").strip()
            spread_str = row.get("spread_remessa", "").strip()
            val_pct = Decimal("0.015")  # Padrão 1.5%
            if spread_str:
                s = spread_str.rstrip("%").replace(",", ".")
                if s.lower() not in ("padrão", "padrao", ""):
                    try:
                        d = Decimal(s)
                        val_pct = d / Decimal("100") if d >= Decimal("0.20") else d
                    except Exception:
                        pass
            contratos_remessa[cnpj] = {
                "lojista": row.get("lojista", "").strip(),
                "spread_contratado_prop": val_pct,
                "obs": row.get("obs", ""),
            }

    # Operações excluídas por taxa negativa (Helena Q&A #7)
    OPS_SPREAD_NEGATIVO: Set[str] = {
        "PC-0926-0210",
        "PC-0926-0326",
        "PC-0926-0491",
        "PC-0926-0545",
    }

    comissoes_por_cliente: Dict[str, Dict[str, Any]] = {}
    divergencias: List[LinhaDivergenciaRemessa] = []
    pendencias: List[LinhaPendenciaRemessa] = []
    rastro: List[LinhaRastroRemessa] = []

    operacoes_vistas: Dict[str, Dict[str, Any]] = {}
    total_comissao_acumulada = Decimal("0.00")

    with open(ponte_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    for row in rows:
        num_op = row.get("num_operacao", "").strip()
        cnpj = row.get("cnpj_cliente", "").strip()
        cliente = row.get("cliente", "").strip()
        spread_brl_str = row.get("spread_brl", "0.00").strip()
        spread_pct_str = row.get("spread_pct", "0.00").strip()
        valor_brl_str = row.get("valor_brl", "0.00").strip()
        obs = row.get("observacao", "").strip()

        spread_brl = Decimal(spread_brl_str) if spread_brl_str else Decimal("0.00")
        spread_pct_aplicado = (Decimal(spread_pct_str) * Decimal("100")) if spread_pct_str else Decimal("0.00")
        valor_brl = Decimal(valor_brl_str) if valor_brl_str else Decimal("0.00")

        # 1. Deduplicação inteligente de operações
        if num_op in operacoes_vistas:
            op_anterior = operacoes_vistas[num_op]
            mesmos_valores = (
                op_anterior["valor_brl"] == valor_brl
                and op_anterior["spread_brl"] == spread_brl
                and op_anterior["cnpj"] == cnpj
            )
            motivo_dup = (
                f"Operação {num_op} duplicada (cópia exata) no relatório da Ponte ('{obs}'). Desconsiderada da apuração."
                if mesmos_valores
                else f"Operação {num_op} duplicada com valores conflitantes no relatório da Ponte (Anterior: {op_anterior['valor_brl']}, Atual: {valor_brl}). Requer auditoria."
            )
            pendencias.append(
                LinhaPendenciaRemessa(
                    tipo="OPERACAO_DUPLICADA",
                    ref_origem=num_op,
                    valor_brl=spread_brl,
                    motivo=motivo_dup,
                    quem_decide="Caio / Helena",
                )
            )
            continue
        operacoes_vistas[num_op] = {
            "valor_brl": valor_brl,
            "spread_brl": spread_brl,
            "cnpj": cnpj,
        }

        # 2. Exclusão de Negativos
        if spread_brl < Decimal("0.00") or num_op in OPS_SPREAD_NEGATIVO:
            pendencias.append(
                LinhaPendenciaRemessa(
                    tipo="SPREAD_NEGATIVO_CONTESTACAO",
                    ref_origem=num_op,
                    valor_brl=abs(spread_brl),
                    motivo=f"Operação com spread negativo ({spread_brl_str} BRL / {obs}). Excluída da comissão/nota para contestação com a Ponte.",
                    quem_decide="Helena",
                )
            )
            continue

        # 3. Cálculo da comissão Tarvo (50% do Spread BRL realizado)
        comissao_tarvo_linha = round_half_up(spread_brl * Decimal("0.50"))
        total_comissao_acumulada += comissao_tarvo_linha

        contrato = contratos_remessa.get(cnpj)
        taxa_contratada_prop = contrato["spread_contratado_prop"] if contrato else Decimal("0.015")
        taxa_contratada_pct = taxa_contratada_prop * Decimal("100")
        regra_aplicada = "Split 50% spread BRL realizado"
        taxa_contratada_str = f"{taxa_contratada_pct:.2f}%"
        detalhe_calc = f"Spread apurado R$ {spread_brl:.2f} * 50% = R$ {comissao_tarvo_linha:.2f}"

        if cnpj not in comissoes_por_cliente:
            nome_lojista = contratos_remessa.get(cnpj, {}).get("lojista", cliente)
            comissoes_por_cliente[cnpj] = {
                "cnpj": cnpj,
                "lojista": nome_lojista,
                "total": Decimal("0.00"),
                "count": 0,
                "refs": [],
            }

        comissoes_por_cliente[cnpj]["total"] += comissao_tarvo_linha
        comissoes_por_cliente[cnpj]["count"] += 1
        comissoes_por_cliente[cnpj]["refs"].append((num_op, comissao_tarvo_linha, regra_aplicada, taxa_contratada_str, detalhe_calc))

        # 4. Auditoria de Taxas (ex: Mundo Aberto: 1.20% acordado vs 1.50% aplicado)
        if contrato:
            spread_contratado_prop = contrato["spread_contratado_prop"]
            spread_contratado_pct = spread_contratado_prop * Decimal("100")
            if (spread_pct_aplicado - spread_contratado_pct) >= Decimal("0.01"):
                # Fórmula canônica Tarvo: valor_me * (taxa_cliente - ptax_ref * (1 + spread_contratado))
                valor_me_str = row.get("valor_me", "0.00").strip()
                taxa_cliente_str = row.get("taxa_cliente", "0.00").strip()
                ptax_ref_str = row.get("ptax_ref", "0.00").strip()
                valor_me = Decimal(valor_me_str) if valor_me_str else Decimal("0.00")
                taxa_cliente = Decimal(taxa_cliente_str) if taxa_cliente_str else Decimal("0.00")
                ptax_ref = Decimal(ptax_ref_str) if ptax_ref_str else Decimal("0.00")

                diff_unitario = taxa_cliente - (ptax_ref * (Decimal("1") + spread_contratado_prop))
                diferenca_cheia = round_half_up(valor_me * diff_unitario)

                divergencias.append(
                    LinhaDivergenciaRemessa(
                        cnpj=cnpj,
                        linha_negocio="REMESSA",
                        ref_origem=num_op,
                        taxa_contratada_pct=spread_contratado_pct.quantize(Decimal("0.01")),
                        taxa_aplicada_pct=spread_pct_aplicado.quantize(Decimal("0.01")),
                        diferenca_brl=diferenca_cheia,
                    )
                )

    lista_comissoes: List[LinhaComissaoRemessa] = []
    for cnpj, dados in sorted(comissoes_por_cliente.items(), key=lambda x: x[1]["lojista"]):
        total_cli = round_half_up(dados["total"])
        lista_comissoes.append(
            LinhaComissaoRemessa(
                cnpj=cnpj,
                lojista=dados["lojista"],
                linha_negocio="REMESSA",
                comissao_brl=total_cli,
                operacoes_count=dados["count"],
            )
        )
        for num_op, v_op, regra, tx_str, det_calc in dados["refs"]:
            rastro.append(
                LinhaRastroRemessa(
                    id_saida=cnpj,
                    arquivo_origem="03_email_ponte_cambio_relatorio_set2026.eml",
                    ref_origem=num_op,
                    valor=v_op,
                    regra_aplicada=regra,
                    taxa_contratada_aplicada=tx_str,
                    detalhe_calculo=det_calc,
                )
            )

    nota_ponte = LinhaNotaRemessa(
        tomador_cnpj="75374179000146",
        tomador="Ponte Câmbio Soluções Financeiras S.A.",
        linha_negocio="REMESSA",
        valor_brl=round_half_up(total_comissao_acumulada),
        discriminacao="Serviços de intermediação e facilitação de remessas internacionais de câmbio (Parceria 50% de spread) - Competência 09/2026.",
    )

    return ResultadoRemessas(
        comissoes=lista_comissoes,
        divergencias=divergencias,
        nota_ponte=nota_ponte,
        pendencias=pendencias,
        rastro=rastro,
        total_comissao_tarvo=round_half_up(total_comissao_acumulada),
    )
