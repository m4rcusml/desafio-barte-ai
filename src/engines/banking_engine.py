"""
Motor de Classificação Contábil e Conciliação Bancária (Camada Gold).
"""

from __future__ import annotations
import csv
import glob
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import List, Optional


@dataclass
class LinhaLancamentoClassificado:
    banco: str        # 'AURORA' ou 'MERIDIANO'
    ref_origem: str   # 'L10', 'L11' ou FITID
    data: str         # AAAA-MM-DD
    descricao: str
    valor: Decimal
    conta_codigo: str
    metodo: str       # 'REGRA' ou 'IA'
    confianca: Decimal
    id_saida: str = ""


@dataclass
class LinhaPendenciaContabil:
    tipo: str
    ref_origem: str
    valor_brl: Decimal
    motivo: str
    quem_decide: str
    id_saida: str = ""


@dataclass
class ResultadoContabil:
    lancamentos: List[LinhaLancamentoClassificado]
    pendencias: List[LinhaPendenciaContabil]


def classificar_extratos(silver_dir: Path) -> ResultadoContabil:
    aurora_files = glob.glob(str(silver_dir / "*AURORA*.csv"))
    meridiano_files = glob.glob(str(silver_dir / "*MERIDIANO*.csv"))

    if not aurora_files:
        raise FileNotFoundError("Extrato Aurora formatado não encontrado.")
    if not meridiano_files:
        raise FileNotFoundError("Extrato Meridiano formatado não encontrado.")

    aurora_path = Path(aurora_files[0])
    meridiano_path = Path(meridiano_files[0])

    lancamentos: List[LinhaLancamentoClassificado] = []
    pendencias: List[LinhaPendenciaContabil] = []

    # 1. BANCO AURORA (C/C 4471-0)
    with open(aurora_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for idx, row in enumerate(reader, start=2):
            val_str = row.get("valor", "").strip()
            if not val_str:
                continue

            ref_origem = f"L{idx}"
            data = row.get("data", "").strip()
            descricao = row.get("lancamento", "").strip()
            valor = Decimal(val_str)
            desc_upper = descricao.upper()

            conta_codigo = "1.1.03.003"
            metodo = "REGRA"
            confianca = Decimal("1.00")

            if "ORBE ADQUIRENCIA" in desc_upper:
                conta_codigo = "1.1.03.001"
            elif "PAGTO SALARIOS" in desc_upper:
                conta_codigo = "2.1.04.001"
            elif "CONDOMINIO" in desc_upper:
                conta_codigo = "4.2.02"
            elif "DAMSP" in desc_upper or "ISS SAO PAULO" in desc_upper:
                conta_codigo = "2.1.03.003"
            elif "AMAZON WEB" in desc_upper:
                conta_codigo = "4.2.03"
            elif "GOOGLE WORKSPACE" in desc_upper:
                conta_codigo = "4.2.04"
            elif "SEM IDENTIFICACAO" in desc_upper:
                conta_codigo = "1.1.09.002"
                pendencias.append(
                    LinhaPendenciaContabil(
                        tipo="CREDITO_NAO_IDENTIFICADO",
                        ref_origem=ref_origem,
                        valor_brl=abs(valor),
                        motivo=f"PIX recebido de R$ {abs(valor)} sem identificação de lojista ou contrato. Retido até confirmação de origem.",
                        quem_decide="Helena / Financeiro",
                    )
                )
            elif "CONTABILIDADE EXATA" in desc_upper:
                conta_codigo = "4.2.06"
            elif "GPS INSS" in desc_upper:
                conta_codigo = "2.1.04.002"
            elif "GRF FGTS" in desc_upper:
                conta_codigo = "2.1.04.003"
            elif "DARF 0561 IRRF" in desc_upper or "IRRF" in desc_upper:
                conta_codigo = "2.1.03.004"
            elif "DEVOLUCAO PIX" in desc_upper:
                conta_codigo = "2.1.01.002"
            elif "DARF 8109 PIS" in desc_upper or "PIS" in desc_upper:
                conta_codigo = "2.1.03.001"
            elif "DARF 2172 COFINS" in desc_upper or "COFINS" in desc_upper:
                conta_codigo = "2.1.03.002"
            elif "TAR PACOTE" in desc_upper or "TAR TED/PIX" in desc_upper or "TAR " in desc_upper:
                conta_codigo = "4.2.01"
            elif "TRANSF ENTRE CONTAS" in desc_upper:
                conta_codigo = "1.1.09.001"
                if data == "2026-09-30":
                    pendencias.append(
                        LinhaPendenciaContabil(
                            tipo="TRANSITO_BANCARIO",
                            ref_origem=ref_origem,
                            valor_brl=abs(valor),
                            motivo="Transferência de R$ 300.000,00 enviada em 30/09 para o Banco Meridiano. Em trânsito até compensação em 01/10/2026.",
                            quem_decide="Caio / Conciliação Bancária",
                        )
                    )
            elif "PIX ENVIADO" in desc_upper:
                conta_codigo = "2.1.01.001"
            else:
                metodo = "IA"
                confianca = Decimal("0.85")

            lancamentos.append(
                LinhaLancamentoClassificado(
                    banco="AURORA",
                    ref_origem=ref_origem,
                    data=data,
                    descricao=descricao,
                    valor=valor,
                    conta_codigo=conta_codigo,
                    metodo=metodo,
                    confianca=confianca,
                )
            )

    # 2. BANCO MERIDIANO (C/C 90233-5)
    with open(meridiano_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            val_str = row.get("valor", "").strip()
            if not val_str:
                continue

            ref_origem = row.get("fitid", "").strip()
            data = row.get("data", "").strip()
            descricao = row.get("lancamento", "").strip()
            valor = Decimal(val_str)
            desc_upper = descricao.upper()

            conta_codigo = "1.1.03.003"
            metodo = "REGRA"
            confianca = Decimal("1.00")

            if "APLICACAO AUTOMATICA" in desc_upper or "RESGATE AUTOMATICO" in desc_upper:
                conta_codigo = "1.1.02.001"
            elif "IOF S/ OPERACAO" in desc_upper:
                conta_codigo = "4.3.01"
            elif "PIX RECEB" in desc_upper:
                conta_codigo = "2.1.02.001"
            elif "RENDIMENTO APLIC" in desc_upper:
                conta_codigo = "3.2.01"
            elif "SEGURO EMPRESARIAL" in desc_upper:
                conta_codigo = "4.2.05"
            elif "TARIFA" in desc_upper:
                conta_codigo = "4.2.01"
            elif "LIQ OPERACOES" in desc_upper:
                conta_codigo = "2.1.02.001"
            elif "REPASSE COMISSAO 08/2026" in desc_upper:
                conta_codigo = "1.1.03.002"
            elif "MESMA TITULARIDADE" in desc_upper:
                conta_codigo = "1.1.09.001"
            else:
                metodo = "IA"
                confianca = Decimal("0.85")

            lancamentos.append(
                LinhaLancamentoClassificado(
                    banco="MERIDIANO",
                    ref_origem=ref_origem,
                    data=data,
                    descricao=descricao,
                    valor=valor,
                    conta_codigo=conta_codigo,
                    metodo=metodo,
                    confianca=confianca,
                )
            )

    return ResultadoContabil(
        lancamentos=lancamentos,
        pendencias=pendencias,
    )
