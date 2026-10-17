"""
Guardrail 1: Detector de Erros, Colisões de ID e Integridade Referencial.
"""

from __future__ import annotations
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ErroValidacao:
    arquivo: str
    linha: int
    campo: str
    valor_invalido: str
    mensagem: str
    gravidade: str  # 'CRITICO' ou 'AVISO'


@dataclass
class RelatorioSanidade:
    arquivos_validados: int = 0
    total_erros: int = 0
    erros_criticos: int = 0
    avisos: int = 0
    detalhes: List[ErroValidacao] = field(default_factory=list)
    valido: bool = True
    colisoes_id: List[Dict[str, str]] = field(default_factory=list)


def validar_silver_files(silver_dir: Path) -> RelatorioSanidade:
    relatorio = RelatorioSanidade()
    detalhes = relatorio.detalhes

    # 1. Checa Orbe Principal
    f_orbe = silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
    orbe_ids: Set[str] = set()

    if f_orbe.exists():
        relatorio.arquivos_validados += 1
        with open(f_orbe, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for idx, row in enumerate(reader, 2):
                tx_id = row.get("id_transacao", "").strip()
                if not tx_id:
                    detalhes.append(ErroValidacao(f_orbe.name, idx, "id_transacao", "", "ID de transação ausente", "CRITICO"))
                    relatorio.erros_criticos += 1
                else:
                    orbe_ids.add(tx_id)

                dt = row.get("data_movimento", "")
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                    detalhes.append(ErroValidacao(f_orbe.name, idx, "data_movimento", dt, "Data fora do padrão ISO AAAA-MM-DD", "CRITICO"))
                    relatorio.erros_criticos += 1

    # 2. Checa Orbe Ajustes Tardios (se presente) e detecta colisões de ID
    f_06 = silver_dir / "06_orbe_ajustes_tardios_formatado.csv"
    if f_06.exists():
        relatorio.arquivos_validados += 1
        with open(f_06, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for idx, row in enumerate(reader, 2):
                tx_id = row.get("id_transacao", "").strip()
                ref_id = row.get("id_referencia", "").strip()
                tipo = row.get("tipo_lancamento", "").strip()

                # Detecção de Colisão de ID com o lote principal
                if tx_id in orbe_ids:
                    relatorio.colisoes_id.append({
                        "id_transacao": tx_id,
                        "arquivo": f_06.name,
                        "linha": str(idx),
                        "acao": "OVERRIDE_PRESERVING_HISTORY",
                    })

                # Integridade referencial: estornos devem apontar para ID válido se houver histórico
                if tipo in ("2", "4") and not ref_id:
                    detalhes.append(ErroValidacao(f_06.name, idx, "id_referencia", "", "Estorno/Reversão sem id_referencia", "AVISO"))
                    relatorio.avisos += 1

    # 3. Checa Taxas
    f_taxas = silver_dir / "02_tabela_taxas_contratadas_formatado.csv"
    if f_taxas.exists():
        relatorio.arquivos_validados += 1
        with open(f_taxas, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for idx, row in enumerate(reader, 2):
                cnpj = row.get("cnpj", "").strip()
                if cnpj and not (len(cnpj) == 14 and cnpj.isdigit()):
                    detalhes.append(ErroValidacao(f_taxas.name, idx, "cnpj", cnpj, "CNPJ deve ter 14 dígitos numéricos", "CRITICO"))
                    relatorio.erros_criticos += 1

    relatorio.total_erros = relatorio.erros_criticos + relatorio.avisos
    relatorio.valido = (relatorio.erros_criticos == 0)
    return relatorio
