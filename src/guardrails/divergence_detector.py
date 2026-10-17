"""
Guardrail 2: Detector de Divergências de Taxa e Consistência de Conciliação.
"""

from __future__ import annotations
from decimal import Decimal
from typing import Dict, List, Any


def filtrar_divergencias_reais(
    divergencias_raw: List[Dict[str, Any]],
    tolerancia_pp: Decimal = Decimal("0.005"),
) -> List[Dict[str, Any]]:
    """
    Filtra divergências de taxa reais eliminando ruído de arredondamento de centavos.
    Regra Helena: centavo de truncamento da adquirente não é divergência;
    divergência é taxa aplicada diferente da taxa contratada.
    """
    divergencias_validas = []
    for d in divergencias_raw:
        diff_pct = abs(Decimal(str(d.get("taxa_aplicada_pct", 0))) - Decimal(str(d.get("taxa_contratada_pct", 0))))
        if diff_pct >= tolerancia_pp:
            divergencias_validas.append(d)
    return divergencias_validas
