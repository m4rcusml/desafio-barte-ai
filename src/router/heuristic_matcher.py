"""
Classificador Heurístico Local - Fast Path & Fallback Determinístico (Camada 3).
Executa em 0.1ms, offline, com 100% de estabilidade e custo zero.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Dict


class HeuristicMatcher:
    """
    Classifica arquivos examinando extensões, nomes e assinaturas de cabeçalho.
    """

    def classify_file(self, filepath: Path, sample_text: str) -> Dict[str, Any]:
        fname = filepath.name.lower()
        sample_lower = sample_text.lower()

        # 1. Ajustes Tardios Orbe (ex: 06_orbe_ajustes_tardios)
        if ("ajuste" in fname or "tardio" in fname or "retroativo" in fname) and ("orbe" in fname or "cod_estabelecimento" in sample_lower):
            return {
                "domain": "ORBE_AJUSTES_TARDIOS",
                "confidence": 1.0,
                "is_delayed_batch": True,
                "delayed_prob": 1.0,
                "method": "HEURISTICA",
            }

        # 2. Orbe Movimentação Principal (01_orbe)
        if "orbe" in fname or ("id_transacao" in sample_lower and "cod_estabelecimento" in sample_lower):
            return {
                "domain": "ORBE_FECHAMENTO_PRINCIPAL",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        # 3. Tabela de Taxas Contratuais (02_tabela_taxas ou .xlsx com taxas)
        if "taxa" in fname or "contrat" in fname or filepath.suffix in (".xlsx", ".xls"):
            return {
                "domain": "TABELA_TAXAS_CONTRATUAIS",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        # 4. E-mail Ponte Câmbio (.eml ou menção a remessas/ponte)
        if filepath.suffix == ".eml" or "ponte" in fname or "cambio" in fname or "remessa" in fname:
            return {
                "domain": "EMAIL_PONTE_CAMBIO",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        # 5. Plano de Contas Fênix ERP
        if "fenix" in fname or "plano" in fname or "conta_contabil" in sample_lower or "4.1." in sample_text:
            return {
                "domain": "PLANO_CONTAS_FENIX",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        # 6. Extrato Banco Aurora
        if "aurora" in fname or "4471" in fname or "4471-0" in sample_text:
            return {
                "domain": "EXTRATO_AURORA",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        # 7. Extrato Banco Meridiano (.ofx ou cc 90233)
        if filepath.suffix == ".ofx" or "meridiano" in fname or "90233" in fname or "<ofx>" in sample_lower:
            return {
                "domain": "EXTRATO_MERIDIANO",
                "confidence": 1.0,
                "is_delayed_batch": False,
                "delayed_prob": 0.0,
                "method": "HEURISTICA",
            }

        return {
            "domain": "DESCONHECIDO",
            "confidence": 0.0,
            "is_delayed_batch": False,
            "delayed_prob": 0.0,
            "method": "HEURISTICA",
        }
