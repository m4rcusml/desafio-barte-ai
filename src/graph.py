"""
Grafo de Orquestração do Fechamento Financeiro (LangGraph).
Coordena os nós de Ingestão, Triagem Tripla, Silver, Guardrails, Engines e Emissão Gold.
"""

from __future__ import annotations
import os
import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Callable

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
from .engines.checkout_engine import processar_checkout, LinhaPendencia, ResultadoCheckout
from .engines.cambio_engine import processar_remessas, LinhaPendenciaRemessa, ResultadoRemessas
from .engines.banking_engine import classificar_extratos, LinhaPendenciaContabil, ResultadoContabil
from .outputs.generator import emitir_todos_os_entregaveis


DOMINIOS_ESPERADOS: Dict[str, Dict[str, Any]] = {
    "ORBE_FECHAMENTO_PRINCIPAL": {
        "frente": "CHECKOUT",
        "dependencia": "TABELA_TAXAS_CONTRATUAIS",
        "responsavel": "Caio / Operações Checkout",
        "obrigatorio": True,
    },
    "ORBE_AJUSTES_TARDIOS": {
        "frente": "CHECKOUT",
        "dependencia": "ORBE_FECHAMENTO_PRINCIPAL, TABELA_TAXAS_CONTRATUAIS",
        "responsavel": "Helena / Conciliação",
        "obrigatorio": False,
    },
    "TABELA_TAXAS_CONTRATUAIS": {
        "frente": "CHECKOUT, REMESSA",
        "dependencia": "Nenhuma (Fonte Mestre de Contratos)",
        "responsavel": "Bia / Comercial",
        "obrigatorio": True,
    },
    "EMAIL_PONTE_CAMBIO": {
        "frente": "REMESSA",
        "dependencia": "TABELA_TAXAS_CONTRATUAIS",
        "responsavel": "Caio / Câmbio",
        "obrigatorio": True,
    },
    "PLANO_CONTAS_FENIX": {
        "frente": "CONTABIL",
        "dependencia": "Nenhuma (Plano de Contas ERP)",
        "responsavel": "Helena / Contabilidade",
        "obrigatorio": True,
    },
    "EXTRATO_AURORA": {
        "frente": "CONTABIL",
        "dependencia": "EXTRATO_MERIDIANO (Conferência de Trânsito)",
        "responsavel": "Caio / Conciliação Bancária",
        "obrigatorio": True,
    },
    "EXTRATO_MERIDIANO": {
        "frente": "CONTABIL",
        "dependencia": "EXTRATO_AURORA (Conferência de Trânsito)",
        "responsavel": "Caio / Conciliação Bancária",
        "obrigatorio": True,
    },
}


# =====================================================================
# NÓS DO GRAFO
# =====================================================================

def node_ingestao_triagem(state: ClosingState) -> ClosingState:
    data_dir = Path(state["data_dir"])
    router = TriTierRouter()
    descobertos = router.scan_directory(data_dir)

    cobertura: Dict[str, Dict[str, Any]] = {}
    for dom_k, meta in DOMINIOS_ESPERADOS.items():
        cobertura[dom_k] = {
            "frente": meta["frente"],
            "estado": "AUSENTE",
            "arquivo": "",
            "motivo": "Fonte ausente no diretório de entrada.",
            "dependencia": meta["dependencia"],
            "responsavel": meta["responsavel"],
            "obrigatorio": meta["obrigatorio"],
            "linhas_validas": 0,
        }

    mapa_arquivos: Dict[str, str] = {}
    orbe_arquivos_lista: List[str] = []

    for item in descobertos:
        dom = item.get("domain")
        caminho = item.get("caminho", "")
        nome = item.get("nome", Path(caminho).name if caminho else "")
        status_item = item.get("status", "VALIDO")

        if dom and dom != "DESCONHECIDO" and status_item != "BLOQUEADO":
            if dom in ("ORBE_FECHAMENTO_PRINCIPAL", "ORBE_AJUSTES_TARDIOS"):
                orbe_arquivos_lista.append(caminho)
            if dom not in mapa_arquivos or ("01" in nome or "06" in nome):
                mapa_arquivos[dom] = caminho
            if dom in cobertura:
                arq_ant = cobertura[dom]["arquivo"]
                cobertura[dom]["arquivo"] = f"{arq_ant}, {nome}" if arq_ant else nome
                cobertura[dom]["estado"] = "IDENTIFICADA"
                cobertura[dom]["motivo"] = "Arquivo identificado na triagem; aguardando formatação Silver."
        else:
            chave_desc = f"DESCONHECIDO:{nome}"
            cobertura[chave_desc] = {
                "frente": "TRIAGEM_INGESTAO",
                "estado": "INVALIDA",
                "arquivo": nome,
                "motivo": item.get("motivo_bloqueio") or f"Arquivo '{nome}' com layout desconhecido ou não reconhecido.",
                "dependencia": "Layout Canônico / Triagem",
                "responsavel": "Helena / Conciliação",
                "obrigatorio": False,
                "linhas_validas": 0,
            }

    state["arquivos_descobertos"] = descobertos
    state["arquivos_identificados"] = mapa_arquivos
    state["cobertura_fontes"] = cobertura
    state["_orbe_arquivos_lista"] = orbe_arquivos_lista  # type: ignore[typeddict-unknown-key]
    return state


def _atualizar_cobertura_pos_formatacao(
    cobertura: Dict[str, Dict[str, Any]],
    dom: str,
    rows_count: int,
    erro: str = "",
) -> None:
    if dom not in cobertura:
        return
    if erro:
        cobertura[dom]["estado"] = "INVALIDA"
        cobertura[dom]["motivo"] = f"Fonte inválida (erro de schema/formatação): {erro}"
        cobertura[dom]["linhas_validas"] = 0
    elif rows_count == 0:
        cobertura[dom]["estado"] = "VALIDA_SEM_MOVIMENTOS"
        cobertura[dom]["motivo"] = "Fonte íntegra e layout válido, porém sem movimentações registradas (0 linhas)."
        cobertura[dom]["linhas_validas"] = 0
    else:
        cobertura[dom]["estado"] = "PROCESSADA"
        cobertura[dom]["motivo"] = f"Fonte validada e processada com {rows_count} registros."
        cobertura[dom]["linhas_validas"] = rows_count


def node_silver_formatters(state: ClosingState) -> ClosingState:
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"
    silver_dir.mkdir(parents=True, exist_ok=True)
    # Limpa arquivos Silver residuais de execuções anteriores no mesmo diretório temporário
    for stale_csv in silver_dir.glob("*.csv"):
        try:
            stale_csv.unlink()
        except Exception:
            pass

    mapa = state.get("arquivos_identificados", {})
    cobertura = state.get("cobertura_fontes", {})
    silver_paths: Dict[str, Any] = {}

    # 1 & 2. Arquivos Orbe (Principal, Ajustes Tardios 06 e eventuais lotes adicionais de outra competência)
    orbe_raw_list: List[str] = state.get("_orbe_arquivos_lista", [])  # type: ignore[assignment]
    if not orbe_raw_list:
        if mapa.get("ORBE_FECHAMENTO_PRINCIPAL"):
            orbe_raw_list.append(mapa["ORBE_FECHAMENTO_PRINCIPAL"])
        if mapa.get("ORBE_AJUSTES_TARDIOS"):
            orbe_raw_list.append(mapa["ORBE_AJUSTES_TARDIOS"])

    orbe_silver_list: List[str] = []
    for idx_o, raw_o in enumerate(orbe_raw_list, start=1):
        p_raw = Path(raw_o)
        low_name = p_raw.name.lower()
        dom_alvo = (
            "ORBE_AJUSTES_TARDIOS"
            if ("06" in low_name or "tardio" in low_name or "ajuste" in low_name)
            else "ORBE_FECHAMENTO_PRINCIPAL"
        )
        if dom_alvo == "ORBE_FECHAMENTO_PRINCIPAL" and "orbe_principal" not in silver_paths:
            out_o = silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
        elif dom_alvo == "ORBE_AJUSTES_TARDIOS" and "orbe_tardios" not in silver_paths:
            out_o = silver_dir / "06_orbe_ajustes_tardios_formatado.csv"
        else:
            out_o = silver_dir / f"orbe_lote_{idx_o}_{p_raw.stem}_formatado.csv"

        try:
            cnt = format_orbe_file(p_raw, out_o)
            orbe_silver_list.append(str(out_o))
            if dom_alvo == "ORBE_FECHAMENTO_PRINCIPAL" and "orbe_principal" not in silver_paths:
                silver_paths["orbe_principal"] = str(out_o)
            elif dom_alvo == "ORBE_AJUSTES_TARDIOS" and "orbe_tardios" not in silver_paths:
                silver_paths["orbe_tardios"] = str(out_o)
            cnt_acum = cobertura.get(dom_alvo, {}).get("linhas_validas", 0) + cnt
            _atualizar_cobertura_pos_formatacao(cobertura, dom_alvo, cnt_acum)
        except Exception as e:
            if out_o.exists():
                out_o.unlink()
            _atualizar_cobertura_pos_formatacao(cobertura, dom_alvo, 0, erro=str(e))

    if orbe_silver_list:
        silver_paths["orbe_files_list"] = orbe_silver_list

    # 3. Taxas Contratuais
    f_taxas = mapa.get("TABELA_TAXAS_CONTRATUAIS")
    if f_taxas:
        out_taxas = silver_dir / "02_tabela_taxas_contratadas_formatado.csv"
        try:
            cnt = format_taxas_file(Path(f_taxas), out_taxas)
            silver_paths["taxas"] = str(out_taxas)
            _atualizar_cobertura_pos_formatacao(cobertura, "TABELA_TAXAS_CONTRATUAIS", cnt)
        except Exception as e:
            if out_taxas.exists():
                out_taxas.unlink()
            _atualizar_cobertura_pos_formatacao(cobertura, "TABELA_TAXAS_CONTRATUAIS", 0, erro=str(e))

    # 4. Ponte Câmbio
    f_ponte = mapa.get("EMAIL_PONTE_CAMBIO")
    if f_ponte:
        out_ponte = silver_dir / "03_ponte_cambio_operacoes_formatado.csv"
        try:
            cnt = format_ponte_file(Path(f_ponte), out_ponte)
            silver_paths["ponte"] = str(out_ponte)
            _atualizar_cobertura_pos_formatacao(cobertura, "EMAIL_PONTE_CAMBIO", cnt)
        except Exception as e:
            if out_ponte.exists():
                out_ponte.unlink()
            _atualizar_cobertura_pos_formatacao(cobertura, "EMAIL_PONTE_CAMBIO", 0, erro=str(e))

    # 5. Fênix ERP
    f_fenix = mapa.get("PLANO_CONTAS_FENIX")
    if f_fenix:
        out_fenix = silver_dir / "04_plano_de_contas_fenix_formatado.csv"
        try:
            cnt = format_fenix_file(Path(f_fenix), out_fenix)
            silver_paths["fenix"] = str(out_fenix)
            _atualizar_cobertura_pos_formatacao(cobertura, "PLANO_CONTAS_FENIX", cnt)
        except Exception as e:
            if out_fenix.exists():
                out_fenix.unlink()
            _atualizar_cobertura_pos_formatacao(cobertura, "PLANO_CONTAS_FENIX", 0, erro=str(e))

    # 6. Extrato Aurora
    f_aurora = mapa.get("EXTRATO_AURORA")
    if f_aurora:
        try:
            p_out, cnt = format_aurora_file(Path(f_aurora), silver_dir)
            silver_paths["aurora"] = str(p_out)
            _atualizar_cobertura_pos_formatacao(cobertura, "EXTRATO_AURORA", cnt)
        except Exception as e:
            _atualizar_cobertura_pos_formatacao(cobertura, "EXTRATO_AURORA", 0, erro=str(e))

    # 7. Extrato Meridiano
    f_meridiano = mapa.get("EXTRATO_MERIDIANO")
    if f_meridiano:
        try:
            p_out, cnt = format_meridiano_file(Path(f_meridiano), silver_dir)
            silver_paths["meridiano"] = str(p_out)
            _atualizar_cobertura_pos_formatacao(cobertura, "EXTRATO_MERIDIANO", cnt)
        except Exception as e:
            _atualizar_cobertura_pos_formatacao(cobertura, "EXTRATO_MERIDIANO", 0, erro=str(e))

    state["silver_paths"] = silver_paths
    state["cobertura_fontes"] = cobertura
    return state


def node_guardrail_1(state: ClosingState) -> ClosingState:
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"
    relatorio = validar_silver_files(silver_dir)
    cobertura = state.get("cobertura_fontes", {})
    silver_paths = state.get("silver_paths", {})

    if not relatorio.valido:
        for det in relatorio.detalhes:
            if det.gravidade == "CRITICO":
                if "01_orbe" in det.arquivo and "ORBE_FECHAMENTO_PRINCIPAL" in cobertura:
                    cobertura["ORBE_FECHAMENTO_PRINCIPAL"]["estado"] = "INVALIDA"
                    cobertura["ORBE_FECHAMENTO_PRINCIPAL"]["motivo"] = (
                        f"Erro crítico no Guardrail 1 ({det.campo}, linha {det.linha}): {det.mensagem}"
                    )
                    silver_paths.pop("orbe_principal", None)
                    silver_paths.pop("orbe_files_list", None)
                elif "02_tabela_taxas" in det.arquivo and "TABELA_TAXAS_CONTRATUAIS" in cobertura:
                    cobertura["TABELA_TAXAS_CONTRATUAIS"]["estado"] = "INVALIDA"
                    cobertura["TABELA_TAXAS_CONTRATUAIS"]["motivo"] = (
                        f"Erro crítico no Guardrail 1 ({det.campo}, linha {det.linha}): {det.mensagem}"
                    )
                    silver_paths.pop("taxas", None)

    state["relatorio_sanidade"] = {
        "valido": relatorio.valido,
        "erros_criticos": relatorio.erros_criticos,
        "avisos": relatorio.avisos,
        "arquivos_validados": relatorio.arquivos_validados,
    }
    state["colisoes_id_detectadas"] = relatorio.colisoes_id
    state["cobertura_fontes"] = cobertura
    state["silver_paths"] = silver_paths
    return state


def node_motores_dominio(state: ClosingState) -> ClosingState:
    silver = state.get("silver_paths", {})
    cobertura = state.get("cobertura_fontes", {})
    competencia = state.get("competencia", "2026-09")
    silver_dir = Path(state.get("output_dir_local", ".")).parent / "dados_formatados"

    # 1. Checkout (consolida lotes Orbe e aplica filtro de competência mantendo referências históricas)
    orbe_files_strs = silver.get("orbe_files_list", [])
    if not orbe_files_strs and "orbe_principal" in silver:
        orbe_files_strs = [silver["orbe_principal"]]
        if "orbe_tardios" in silver:
            orbe_files_strs.append(silver["orbe_tardios"])

    if "taxas" in silver and orbe_files_strs:
        tabela_taxas_p = Path(silver["taxas"])
        orbe_files = [Path(p) for p in orbe_files_strs]
        res_checkout = processar_checkout(orbe_files, tabela_taxas_p, competencia=competencia)
    else:
        res_checkout = ResultadoCheckout(comissoes=[], divergencias=[], pendencias=[], rastro=[], totais_por_lojista={})
        if orbe_files_strs and "taxas" not in silver:
            arq_orbe_nome = cobertura.get("ORBE_FECHAMENTO_PRINCIPAL", {}).get("arquivo") or "01_orbe_relatorio_comissoes_set2026.csv"
            if "ORBE_FECHAMENTO_PRINCIPAL" in cobertura:
                cobertura["ORBE_FECHAMENTO_PRINCIPAL"]["estado"] = "BLOQUEADA_POR_DEPENDENCIA"
                cobertura["ORBE_FECHAMENTO_PRINCIPAL"]["motivo"] = (
                    "Frente CHECKOUT bloqueada: TABELA_TAXAS_CONTRATUAIS ausente ou inválida."
                )
            res_checkout.pendencias.append(
                LinhaPendencia(
                    tipo="FONTE_DEPENDENTE_AUSENTE",
                    ref_origem=arq_orbe_nome,
                    valor_brl=Decimal("0.00"),
                    motivo="Frente CHECKOUT bloqueada: arquivo Orbe presente, mas TABELA_TAXAS_CONTRATUAIS está ausente ou inválida.",
                    quem_decide="Bia / Comercial",
                    arquivo_origem=arq_orbe_nome,
                )
            )

    # 2. Câmbio
    if "taxas" in silver and "ponte" in silver:
        tabela_taxas_p = Path(silver["taxas"])
        ponte_p = Path(silver["ponte"])
        res_remessas = processar_remessas(ponte_p, tabela_taxas_p, competencia=competencia)
    else:
        res_remessas = ResultadoRemessas(comissoes=[], divergencias=[], pendencias=[], rastro=[], nota_ponte=None)
        if "ponte" in silver and "taxas" not in silver:
            arq_ponte_nome = cobertura.get("EMAIL_PONTE_CAMBIO", {}).get("arquivo") or "03_email_ponte_cambio_relatorio_set2026.eml"
            if "EMAIL_PONTE_CAMBIO" in cobertura:
                cobertura["EMAIL_PONTE_CAMBIO"]["estado"] = "BLOQUEADA_POR_DEPENDENCIA"
                cobertura["EMAIL_PONTE_CAMBIO"]["motivo"] = (
                    "Frente REMESSA bloqueada: TABELA_TAXAS_CONTRATUAIS ausente ou inválida."
                )
            res_remessas.pendencias.append(
                LinhaPendenciaRemessa(
                    tipo="FONTE_DEPENDENTE_AUSENTE",
                    ref_origem=arq_ponte_nome,
                    valor_brl=Decimal("0.00"),
                    motivo="Frente REMESSA bloqueada: relatório Ponte presente, mas TABELA_TAXAS_CONTRATUAIS está ausente ou inválida.",
                    quem_decide="Bia / Comercial",
                    arquivo_origem=arq_ponte_nome,
                )
            )

    # 3. Bancário
    if "aurora" in silver and "meridiano" in silver:
        try:
            res_contabil = classificar_extratos(silver_dir, competencia=competencia)
        except Exception as e:
            res_contabil = ResultadoContabil(lancamentos=[], pendencias=[])
            cobertura["EXTRATO_AURORA"]["estado"] = "INVALIDA"
            cobertura["EXTRATO_AURORA"]["motivo"] = f"Erro na conciliação bancária: {e}"
    else:
        res_contabil = ResultadoContabil(lancamentos=[], pendencias=[])
        if ("aurora" in silver) ^ ("meridiano" in silver):
            dom_presente = "EXTRATO_AURORA" if "aurora" in silver else "EXTRATO_MERIDIANO"
            dom_faltante = "EXTRATO_MERIDIANO" if "aurora" in silver else "EXTRATO_AURORA"
            arq_pres = cobertura.get(dom_presente, {}).get("arquivo") or dom_presente
            if dom_presente in cobertura:
                cobertura[dom_presente]["estado"] = "BLOQUEADA_POR_DEPENDENCIA"
                cobertura[dom_presente]["motivo"] = (
                    f"Conciliação bancária cruzada bloqueada: {dom_faltante} ausente ou inválido."
                )
            res_contabil.pendencias.append(
                LinhaPendenciaContabil(
                    tipo="FONTE_DEPENDENTE_AUSENTE",
                    ref_origem=arq_pres,
                    valor_brl=Decimal("0.00"),
                    motivo=f"Frente CONTÁBIL bloqueada para conciliação de trânsito: {dom_presente} presente, mas {dom_faltante} está ausente ou inválido.",
                    quem_decide="Caio / Conciliação Bancária",
                    arquivo_origem=arq_pres,
                )
            )

    # 4. Fontes inválidas ou de layout desconhecido geram pendência explícita (nunca viram zero silencioso)
    for dom_k, cob_v in cobertura.items():
        if cob_v.get("estado") == "INVALIDA":
            ref_inv = cob_v.get("arquivo") or dom_k
            res_checkout.pendencias.append(
                LinhaPendencia(
                    tipo="FONTE_INVALIDA_OU_LAYOUT_DESCONHECIDO",
                    ref_origem=ref_inv,
                    valor_brl=Decimal("0.00"),
                    motivo=f"Fonte '{ref_inv}' ({dom_k}) bloqueada: {cob_v.get('motivo')}",
                    quem_decide=cob_v.get("responsavel", "Helena / Conciliação"),
                    arquivo_origem=ref_inv,
                )
            )

    # 5. Determinação do estado_tecnico da execução
    alguma_invalida_ou_bloqueada = any(
        v.get("estado") in ("INVALIDA", "BLOQUEADA_POR_DEPENDENCIA")
        for v in cobertura.values()
    )
    alguma_obrigatoria_ausente = any(
        v.get("obrigatorio") and v.get("estado") == "AUSENTE"
        for v in cobertura.values()
    )
    state["estado_tecnico"] = (
        "PARCIAL_COM_BLOQUEIOS"
        if (alguma_invalida_ou_bloqueada or alguma_obrigatoria_ausente)
        else "CONCLUIDO"
    )
    state["cobertura_fontes"] = cobertura
    state["resultado_checkout"] = res_checkout
    state["resultado_cambio"] = res_remessas
    state["resultado_bancario"] = res_contabil
    return state


def node_guardrail_2(state: ClosingState) -> ClosingState:
    res_checkout = state.get("resultado_checkout")
    if res_checkout and res_checkout.divergencias:
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
