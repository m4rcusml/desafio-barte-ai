"""
Motor de Remessas e Câmbio (Camada Gold).
"""

from __future__ import annotations
import csv
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from ..utils import round_half_up, format_competencia_br


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
    arquivo_origem: str = ""


@dataclass
class LinhaNotaRemessa:
    tomador_cnpj: str
    tomador: str
    linha_negocio: str
    valor_brl: Decimal
    discriminacao: str
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
class LinhaPendenciaRemessa:
    tipo: str
    ref_origem: str
    valor_brl: Decimal
    motivo: str
    quem_decide: str
    id_saida: str = ""
    arquivo_origem: str = "03_email_ponte_cambio_relatorio_set2026.eml"
    rastro_itens: List[LinhaRastroRemessa] = field(default_factory=list)


@dataclass
class ResultadoRemessas:
    comissoes: List[LinhaComissaoRemessa]
    divergencias: List[LinhaDivergenciaRemessa]
    nota_ponte: LinhaNotaRemessa
    pendencias: List[LinhaPendenciaRemessa]
    rastro: List[LinhaRastroRemessa]
    total_comissao_tarvo: Decimal = Decimal("0.00")


def _assinatura_operacao_ponte(row: Dict[str, str]) -> Tuple[Any, ...]:
    """Retorna tupla canônica com todos os campos financeiros e operacionais relevantes da Ponte."""
    cnpj = row.get("cnpj_cliente", "").strip()
    data_cont = row.get("data_contratacao", "").strip()
    data_liq = row.get("data_liquidacao", "").strip()
    moeda = row.get("moeda", "").strip()
    valor_me = round_half_up(Decimal(row.get("valor_me", "0.00").strip() or "0.00"))
    taxa_cli = Decimal(row.get("taxa_cliente", "0.00").strip() or "0.00")
    ptax_ref = Decimal(row.get("ptax_ref", "0.00").strip() or "0.00")
    valor_brl = round_half_up(Decimal(row.get("valor_brl", "0.00").strip() or "0.00"))
    spread_brl = round_half_up(Decimal(row.get("spread_brl", "0.00").strip() or "0.00"))
    spread_pct = Decimal(row.get("spread_pct", "0.00").strip() or "0.00")
    iof_brl = round_half_up(Decimal(row.get("iof_brl", "0.00").strip() or "0.00"))
    return (
        cnpj,
        data_cont,
        data_liq,
        moeda,
        valor_me,
        taxa_cli,
        ptax_ref,
        valor_brl,
        spread_brl,
        spread_pct,
        iof_brl,
    )


def processar_remessas(
    ponte_csv_path: Path,
    tabela_taxas_path: Path,
    competencia: Optional[str] = None,
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

    total_comissao_acumulada = Decimal("0.00")
    arq_ponte_orig = ponte_csv_path.name

    with open(ponte_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
    if rows:
        arq_ponte_orig = rows[0].get("arquivo_origem") or arq_ponte_orig

    # Pré-passo de agrupamento por num_operacao para detectar duplicatas exatas vs conflitantes
    # antes de acumular qualquer comissão, divergência ou nota fiscal (evita First-Write-Wins).
    grupos_op: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        num_op = row.get("num_operacao", "").strip()
        if not num_op:
            continue
        grupos_op.setdefault(num_op, []).append(row)

    ops_ja_processadas: Set[str] = set()

    for row in rows:
        num_op = row.get("num_operacao", "").strip()
        if not num_op or num_op in ops_ja_processadas:
            continue

        ocorrencias = grupos_op[num_op]

        # Filtro de competência por data_contratacao (quando informada nos registros)
        if competencia:
            datas_grupo = [
                r_oc.get("data_contratacao", "").strip()
                for r_oc in ocorrencias
                if r_oc.get("data_contratacao", "").strip()
            ]
            if datas_grupo and not any(d.startswith(competencia) for d in datas_grupo):
                ops_ja_processadas.add(num_op)
                continue

        ops_ja_processadas.add(num_op)

        # 1. Verificação de duplicidade exata vs conflitante
        sufixo_dedup = ""
        if len(ocorrencias) > 1:
            assinaturas = [_assinatura_operacao_ponte(r_oc) for r_oc in ocorrencias]
            if len(set(assinaturas)) > 1:
                # Conflito de dados entre registros com mesmo num_operacao: bloqueia TODAS as versões!
                rastro_conflito: List[LinhaRastroRemessa] = []
                desc_versoes: List[str] = []
                for idx_oc, r_oc in enumerate(ocorrencias, start=1):
                    vb_oc = round_half_up(Decimal(r_oc.get("valor_brl", "0.00").strip() or "0.00"))
                    sb_oc = round_half_up(Decimal(r_oc.get("spread_brl", "0.00").strip() or "0.00"))
                    cnpj_oc = r_oc.get("cnpj_cliente", "").strip()
                    desc_versoes.append(
                        f"v{idx_oc} (cnpj={cnpj_oc}, valor_brl=R$ {vb_oc:.2f}, spread_brl=R$ {sb_oc:.2f})"
                    )
                    rastro_conflito.append(
                        LinhaRastroRemessa(
                            id_saida="",
                            arquivo_origem=arq_ponte_orig,
                            ref_origem=num_op,
                            valor=abs(sb_oc),
                            regra_aplicada="Bloqueio integral por duplicidade conflitante na Ponte Câmbio",
                            taxa_contratada_aplicada="BLOQUEADO",
                            detalhe_calculo=f"Versão {idx_oc} conflitante: valor_brl R$ {vb_oc:.2f}, spread_brl R$ {sb_oc:.2f}",
                        )
                    )
                val_bloqueado = round_half_up(sum(item.valor for item in rastro_conflito))
                pendencias.append(
                    LinhaPendenciaRemessa(
                        tipo="OPERACAO_DUPLICADA",
                        ref_origem=num_op,
                        valor_brl=val_bloqueado,
                        motivo=(
                            f"Operação {num_op} duplicada com valores conflitantes no relatório da Ponte "
                            f"[{'; '.join(desc_versoes)}]. Todas as ocorrências foram bloqueadas sem escolha automática."
                        ),
                        quem_decide="Helena / Conciliação",
                        arquivo_origem=arq_ponte_orig,
                        rastro_itens=rastro_conflito,
                    )
                )
                continue
            else:
                # Cópia exata: processa a 1ª ocorrência normalmente e registra pendência documental para cada cópia descartada
                sufixo_dedup = f" [Deduplicado: {len(ocorrencias)} ocorrências idênticas]"
                for r_dup in ocorrencias[1:]:
                    sb_dup = round_half_up(Decimal(r_dup.get("spread_brl", "0.00").strip() or "0.00"))
                    obs_dup = r_dup.get("observacao", "").strip()
                    pendencias.append(
                        LinhaPendenciaRemessa(
                            tipo="OPERACAO_DUPLICADA",
                            ref_origem=num_op,
                            valor_brl=sb_dup,
                            motivo=f"Operação {num_op} duplicada (cópia exata) no relatório da Ponte ('{obs_dup}'). Desconsiderada da apuração.",
                            quem_decide="Caio / Helena",
                            arquivo_origem=arq_ponte_orig,
                            rastro_itens=[
                                LinhaRastroRemessa(
                                    id_saida="",
                                    arquivo_origem=arq_ponte_orig,
                                    ref_origem=num_op,
                                    valor=sb_dup,
                                    regra_aplicada="Descarte de cópia exata na Ponte Câmbio",
                                    taxa_contratada_aplicada="N/A",
                                    detalhe_calculo=f"Cópia exata descartada ('{obs_dup}'): spread R$ {sb_dup:.2f}",
                                )
                            ],
                        )
                    )

        cnpj = row.get("cnpj_cliente", "").strip()
        cliente = row.get("cliente", "").strip()
        spread_brl_str = row.get("spread_brl", "0.00").strip()
        spread_pct_str = row.get("spread_pct", "0.00").strip()
        valor_brl_str = row.get("valor_brl", "0.00").strip()
        obs = row.get("observacao", "").strip()

        spread_brl = Decimal(spread_brl_str) if spread_brl_str else Decimal("0.00")
        spread_pct_aplicado = (Decimal(spread_pct_str) * Decimal("100")) if spread_pct_str else Decimal("0.00")
        valor_brl = Decimal(valor_brl_str) if valor_brl_str else Decimal("0.00")

        # 2. Exclusão de Negativos
        if spread_brl < Decimal("0.00") or num_op in OPS_SPREAD_NEGATIVO:
            val_neg = round_half_up(abs(spread_brl))
            pendencias.append(
                LinhaPendenciaRemessa(
                    tipo="SPREAD_NEGATIVO_CONTESTACAO",
                    ref_origem=num_op,
                    valor_brl=val_neg,
                    motivo=f"Operação com spread negativo ({spread_brl_str} BRL / {obs}). Excluída da comissão/nota para contestação com a Ponte.",
                    quem_decide="Helena",
                    arquivo_origem=arq_ponte_orig,
                    rastro_itens=[
                        LinhaRastroRemessa(
                            id_saida="",
                            arquivo_origem=arq_ponte_orig,
                            ref_origem=num_op,
                            valor=val_neg,
                            regra_aplicada="Exclusão e contestação de operação com spread negativo",
                            taxa_contratada_aplicada="N/A",
                            detalhe_calculo=f"Spread negativo reportado: {spread_brl_str} BRL ({obs})",
                        )
                    ],
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
        detalhe_calc = f"Spread apurado R$ {spread_brl:.2f} * 50% = R$ {comissao_tarvo_linha:.2f}{sufixo_dedup}"

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
                        arquivo_origem=arq_ponte_orig,
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
                    arquivo_origem=arq_ponte_orig,
                    ref_origem=num_op,
                    valor=v_op,
                    regra_aplicada=regra,
                    taxa_contratada_aplicada=tx_str,
                    detalhe_calculo=det_calc,
                )
            )

    comp_label = format_competencia_br(competencia)
    nota_ponte = LinhaNotaRemessa(
        tomador_cnpj="75374179000146",
        tomador="Ponte Câmbio Soluções Financeiras S.A.",
        linha_negocio="REMESSA",
        valor_brl=round_half_up(total_comissao_acumulada),
        discriminacao=f"Serviços de intermediação e facilitação de remessas internacionais de câmbio (Parceria 50% de spread) - Competência {comp_label}.",
    )

    return ResultadoRemessas(
        comissoes=lista_comissoes,
        divergencias=divergencias,
        nota_ponte=nota_ponte,
        pendencias=pendencias,
        rastro=rastro,
        total_comissao_tarvo=round_half_up(total_comissao_acumulada),
    )

