"""
Grafo de Orquestração do Fechamento Financeiro (LangGraph).
Coordena os nós de Ingestão, Triagem Tripla, Silver, Guardrails, Engines e Emissão Gold.
"""

from __future__ import annotations
import os
import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Callable

from .state import ClosingState
from .router.triage import TriTierRouter
from .formatters.orbe_formatter import format_orbe_file
from .formatters.taxas_formatter import format_taxas_file
from .formatters.ponte_formatter import format_ponte_file
from .formatters.fenix_formatter import format_fenix_file
from .formatters.aurora_formatter import format_aurora_file
from .formatters.meridiano_formatter import format_meridiano_file
from .guardrails.error_detector import validar_silver_files
from .guardrails.divergence_detector import filtrar_divergencias_reais
from .engines.checkout_engine import processar_checkout
from .engines.cambio_engine import processar_remessas
from .engines.banking_engine import classificar_extratos
from .outputs.generator import emitir_todos_os_entregaveis


# =====================================================================
# NÓS DO GRAFO
# =====================================================================

def node_ingestao_triagem(state: ClosingState) -> ClosingState:
    data_dir = Path(state["data_dir"])
    router = TriTierRouter()
    descobertos = router.scan_directory(data_dir)

    mapa_arquivos = {}
    for item in descobertos:
        dom = item.get("domain")
        if dom and dom != "DESCONHECIDO":
            mapa_arquivos[dom] = item.get("caminho")

    state["arquivos_descobertos"] = descobertos
    state["arquivos_identificados"] = mapa_arquivos
    return state


def node_silver_formatters(state: ClosingState) -> ClosingState:
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"
    silver_dir.mkdir(parents=True, exist_ok=True)

    mapa = state.get("arquivos_identificados", {})
    silver_paths = {}

    # 1. Orbe Principal
    f_orbe = mapa.get("ORBE_FECHAMENTO_PRINCIPAL")
    if f_orbe:
        out_p = silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
        format_orbe_file(Path(f_orbe), out_p)
        silver_paths["orbe_principal"] = str(out_p)

    # 2. Orbe Ajustes Tardios (06)
    f_06 = mapa.get("ORBE_AJUSTES_TARDIOS")
    if f_06:
        out_06 = silver_dir / "06_orbe_ajustes_tardios_formatado.csv"
        format_orbe_file(Path(f_06), out_06)
        silver_paths["orbe_tardios"] = str(out_06)

    # 3. Taxas Contratuais
    f_taxas = mapa.get("TABELA_TAXAS_CONTRATUAIS")
    if f_taxas:
        out_taxas = silver_dir / "02_tabela_taxas_contratadas_formatado.csv"
        format_taxas_file(Path(f_taxas), out_taxas)
        silver_paths["taxas"] = str(out_taxas)

    # 4. Ponte Câmbio
    f_ponte = mapa.get("EMAIL_PONTE_CAMBIO")
    if f_ponte:
        out_ponte = silver_dir / "03_ponte_cambio_operacoes_formatado.csv"
        format_ponte_file(Path(f_ponte), out_ponte)
        silver_paths["ponte"] = str(out_ponte)

    # 5. Fênix ERP
    f_fenix = mapa.get("PLANO_CONTAS_FENIX")
    if f_fenix:
        out_fenix = silver_dir / "04_plano_de_contas_fenix_formatado.csv"
        format_fenix_file(Path(f_fenix), out_fenix)
        silver_paths["fenix"] = str(out_fenix)

    # 6. Extrato Aurora
    f_aurora = mapa.get("EXTRATO_AURORA")
    if f_aurora:
        p_out, _ = format_aurora_file(Path(f_aurora), silver_dir)
        silver_paths["aurora"] = str(p_out)

    # 7. Extrato Meridiano
    f_meridiano = mapa.get("EXTRATO_MERIDIANO")
    if f_meridiano:
        p_out, _ = format_meridiano_file(Path(f_meridiano), silver_dir)
        silver_paths["meridiano"] = str(p_out)

    state["silver_paths"] = silver_paths
    return state


def node_guardrail_1(state: ClosingState) -> ClosingState:
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"
    relatorio = validar_silver_files(silver_dir)

    state["relatorio_sanidade"] = {
        "valido": relatorio.valido,
        "erros_criticos": relatorio.erros_criticos,
        "avisos": relatorio.avisos,
        "arquivos_validados": relatorio.arquivos_validados,
    }
    state["colisoes_id_detectadas"] = relatorio.colisoes_id
    return state


def node_motores_dominio(state: ClosingState) -> ClosingState:
    silver = state.get("silver_paths", {})
    tabela_taxas_p = Path(silver["taxas"])

    # 1. Checkout (consolida 01 e 06 em setembro conforme AGENTS.md)
    orbe_files = [Path(silver["orbe_principal"])]
    if "orbe_tardios" in silver:
        orbe_files.append(Path(silver["orbe_tardios"]))

    res_checkout = processar_checkout(orbe_files, tabela_taxas_p)

    # Se houve colisão de IDs no Guardrail 1, injeta na lista de pendências para a Helena
    for col in state.get("colisoes_id_detectadas", []):
        from .engines.checkout_engine import LinhaPendencia
        res_checkout.pendencias.append(
            LinhaPendencia(
                tipo="CONFLITO_ID_TRANSACAO",
                ref_origem=col["id_transacao"],
                valor_brl=Decimal("0.00"),
                motivo=f"ID {col['id_transacao']} presente no lote principal retificado por ajuste tardio. Requer validação.",
                quem_decide="Helena",
            )
        )

    # 2. Câmbio
    ponte_p = Path(silver["ponte"])
    res_remessas = processar_remessas(ponte_p, tabela_taxas_p)

    # 3. Bancário
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"
    res_contabil = classificar_extratos(silver_dir)

    state["resultado_checkout"] = res_checkout
    state["resultado_cambio"] = res_remessas
    state["resultado_bancario"] = res_contabil
    return state


def node_guardrail_2(state: ClosingState) -> ClosingState:
    res_checkout = state["resultado_checkout"]
    # Garante auditoria de divergências reais
    res_checkout.divergencias = [
        d for d in res_checkout.divergencias
        if abs(d.taxa_aplicada_pct - d.taxa_contratada_pct) >= Decimal("0.005")
    ]
    return state


def node_emissor_gold(state: ClosingState) -> ClosingState:
    output_local = Path(state["output_dir_local"])
    output_oficial = Path(state["output_dir_oficial"])

    summary = emitir_todos_os_entregaveis(
        res_checkout=state["resultado_checkout"],
        res_remessas=state["resultado_cambio"],
        res_contabil=state["resultado_bancario"],
        output_dir_local=output_local,
        output_dir_oficial=output_oficial,
        state=state,
    )

    state["resumo_execucao"] = summary
    state["prova_real_valida"] = summary.get("prova_real_valida", True)
    return state


# =====================================================================
# DEFINIÇÃO DO GRAFO (DUAL-MODE: LangGraph / Native StateGraph)
# =====================================================================

class NativeStateGraph:
    """Implementação canônica de StateGraph compatível com LangGraph."""
    def __init__(self, state_schema):
        self.state_schema = state_schema
        self.nodes: Dict[str, Callable] = {}
        self.edges: List[tuple] = []
        self.entry_point = None

    def add_node(self, name: str, func: Callable):
        self.nodes[name] = func

    def add_edge(self, from_node: str, to_node: str):
        if self.entry_point is None:
            self.entry_point = from_node
        self.edges.append((from_node, to_node))

    def set_entry_point(self, name: str):
        self.entry_point = name

    def compile(self):
        return self

    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        curr = self.entry_point
        visited = set()
        while curr:
            node_fn = self.nodes.get(curr)
            if node_fn:
                state = node_fn(state)
            # Encontra próximo
            next_nodes = [t for f, t in self.edges if f == curr]
            if not next_nodes or next_nodes[0] == "__end__":
                break
            curr = next_nodes[0]
        return state


def build_closing_graph():
    """Constrói e compila o grafo de fechamento financeiro."""
    try:
        from langgraph.graph import StateGraph, START, END
        builder = StateGraph(ClosingState)
        builder.add_node("ingestao_triagem", node_ingestao_triagem)
        builder.add_node("silver_formatters", node_silver_formatters)
        builder.add_node("guardrail_1", node_guardrail_1)
        builder.add_node("motores_dominio", node_motores_dominio)
        builder.add_node("guardrail_2", node_guardrail_2)
        builder.add_node("emissor_gold", node_emissor_gold)

        builder.add_edge(START, "ingestao_triagem")
        builder.add_edge("ingestao_triagem", "silver_formatters")
        builder.add_edge("silver_formatters", "guardrail_1")
        builder.add_edge("guardrail_1", "motores_dominio")
        builder.add_edge("motores_dominio", "guardrail_2")
        builder.add_edge("guardrail_2", "emissor_gold")
        builder.add_edge("emissor_gold", END)
        return builder.compile()
    except ImportError:
        # Fallback para o motor de StateGraph nativo
        graph = NativeStateGraph(ClosingState)
        graph.add_node("ingestao_triagem", node_ingestao_triagem)
        graph.add_node("silver_formatters", node_silver_formatters)
        graph.add_node("guardrail_1", node_guardrail_1)
        graph.add_node("motores_dominio", node_motores_dominio)
        graph.add_node("guardrail_2", node_guardrail_2)
        graph.add_node("emissor_gold", node_emissor_gold)

        graph.set_entry_point("ingestao_triagem")
        graph.add_edge("ingestao_triagem", "silver_formatters")
        graph.add_edge("silver_formatters", "guardrail_1")
        graph.add_edge("guardrail_1", "motores_dominio")
        graph.add_edge("motores_dominio", "guardrail_2")
        graph.add_edge("guardrail_2", "emissor_gold")
        graph.add_edge("emissor_gold", "__end__")
        return graph.compile()
