"""
Estado Tipado do Fechamento Financeiro (LangGraph State).
Gerencia os dados e artefatos ao longo de todos os nós do grafo.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict


class FileMetadata(TypedDict, total=False):
    caminho: str
    nome: str
    extensao: str
    dominio: str           # 'ORBE_CHECKOUT', 'ORBE_AJUSTES_TARDIOS', 'PONTE_CAMBIO', 'EXTRATO_AURORA', 'EXTRATO_MERIDIANO', 'PLANO_FENIX', 'TABELA_TAXAS'
    confianca: float
    metodo_triagem: str    # 'JEV', 'GEMINI_FLASH', 'HEURISTICA'
    status: str            # 'VALIDO', 'AVISO', 'BLOQUEADO'
    motivo_bloqueio: Optional[str]


class ClosingState(TypedDict, total=False):
    # Contexto de Execução
    data_dir: str
    output_dir_local: str       # fechamento-completo/ ao lado do executável
    output_dir_oficial: str     # barte-solution/desafio-barte-ai/saida
    status_aprovacao: str       # 'PROVISORIO' ou 'APROVADO_POR_HELENA'
    competencia: str            # '2026-09'

    # Ingestão e Triagem Tripla
    arquivos_descobertos: List[FileMetadata]
    arquivos_identificados: Dict[str, str]  # chave semântica -> caminho do arquivo

    # Camada Silver (dados formatados canônicos)
    silver_paths: Dict[str, str]
    relatorio_sanidade: Dict[str, Any]
    colisoes_id_detectadas: List[Dict[str, Any]]

    # Resultados dos Motores de Domínio
    resultado_checkout: Dict[str, Any]
    resultado_cambio: Dict[str, Any]
    resultado_bancario: Dict[str, Any]

    # Guardrail 2 (Divergências e Conciliações)
    divergencias_apuradas: List[Dict[str, Any]]
    pendencias_operacionais: List[Dict[str, Any]]
    classificacoes_contabeis: List[Dict[str, Any]]

    # Entregáveis Oficiais (Camada Gold)
    comissoes_por_lojista: List[Dict[str, Any]]
    notas_a_emitir: List[Dict[str, Any]]
    rastro_completo: List[Dict[str, Any]]
    resumo_execucao: Dict[str, Any]
    prova_real_valida: bool
