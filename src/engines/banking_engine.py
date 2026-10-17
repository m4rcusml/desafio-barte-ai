"""
Motor de Classificação Contábil e Conciliação Bancária (Camada Gold).
"""

from __future__ import annotations
import csv
import glob
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Set, Tuple


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

    # 1. Pré-leitura do BANCO MERIDIANO (C/C 90233-5) para conferência de trânsito bancário
    meridiano_rows: List[Dict[str, str]] = []
    meridiano_creditos_mesma_titularidade: Set[Tuple[str, Decimal]] = set()

    with open(meridiano_path, mode="r", encoding="utf-8") as f:
        reader_m = csv.DictReader(f, delimiter=";")
        for r in reader_m:
            meridiano_rows.append(r)
            v_s = r.get("valor", "").strip()
            if not v_s:
                continue
            v_dec = Decimal(v_s)
            d_s = r.get("data", "").strip()
            desc = r.get("lancamento", "").strip().upper()
            if "MESMA TITULARIDADE" in desc and v_dec > Decimal("0.00"):
                meridiano_creditos_mesma_titularidade.add((d_s, v_dec))

    # 2. BANCO AURORA (C/C 4471-0)
    with open(aurora_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for idx, row in enumerate(reader, start=2):
            val_str = row.get("valor", "").strip()
            if not val_str:
                continue

            linha_fisica = row.get("linha_fisica", "").strip()
            ref_origem = f"L{linha_fisica}" if linha_fisica else f"L{idx}"
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
            elif "CONTABILIDADE" in desc_upper:
                conta_codigo = "4.2.06"
            elif "GPS INSS" in desc_upper:
                conta_codigo = "2.1.04.002"
            elif "GRF FGTS" in desc_upper:
                conta_codigo = "2.1.04.003"
            elif "DARF 0561 IRRF" in desc_upper or "IRRF" in desc_upper:
                conta_codigo = "2.1.03.004"
            elif "DEVOLUCAO PIX" in desc_upper:
                conta_codigo = "2.1.01.001"
                pendencias.append(
                    LinhaPendenciaContabil(
                        tipo="DEVOLUCAO_SEM_CAUSA",
                        ref_origem=ref_origem,
                        valor_brl=abs(valor),
                        motivo=f"Devolução de PIX Mundo Aberto (R$ {abs(valor):.2f}): repasse operacional retornado sem causa informada. Aguarda apuração.",
                        quem_decide="Helena / Comercial",
                    )
                )
            elif "DARF 8109 PIS" in desc_upper or "PIS" in desc_upper:
                conta_codigo = "2.1.03.001"
            elif "DARF 2172 COFINS" in desc_upper or "COFINS" in desc_upper:
                conta_codigo = "2.1.03.002"
            elif "TAR PACOTE" in desc_upper or "TAR TED/PIX" in desc_upper or "TAR " in desc_upper:
                conta_codigo = "4.2.01"
            elif "TRANSF ENTRE CONTAS" in desc_upper:
                conta_codigo = "1.1.09.001"
                # Verificação dinâmica: houve crédito de mesma titularidade de mesmo valor e mesma data no Meridiano?
                valor_debito_pos = abs(valor)
                if (data, valor_debito_pos) not in meridiano_creditos_mesma_titularidade:
                    pendencias.append(
                        LinhaPendenciaContabil(
                            tipo="TRANSITO_BANCARIO",
                            ref_origem=ref_origem,
                            valor_brl=valor_debito_pos,
                            motivo=f"Transferência de R$ {valor_debito_pos:.2f} enviada em {data} para o Banco Meridiano não compensada no mesmo dia. Em trânsito bancário até compensação.",
                            quem_decide="Caio / Conciliação Bancária",
                        )
                    )
            elif "PIX ENVIADO" in desc_upper:
                conta_codigo = "2.1.01.001"
                if "ATLAS" in desc_upper:
                    pendencias.append(
                        LinhaPendenciaContabil(
                            tipo="REPASSE_LOJISTA_BLOQUEADO",
                            ref_origem=ref_origem,
                            valor_brl=abs(valor),
                            motivo=f"Repasse via PIX de R$ {abs(valor):.2f} enviado para Atlas Idiomas (Lojista bloqueado para faturamento por ausência de contrato assinado). Requer averiguação da diretoria/comercial.",
                            quem_decide="Helena / Comercial",
                        )
                    )
            else:
                metodo = "HUMANO"
                confianca = Decimal("0.00")
                conta_codigo = "1.1.09.002"
                pendencias.append(
                    LinhaPendenciaContabil(
                        tipo="LANCAMENTO_SEM_REGRA",
                        ref_origem=ref_origem,
                        valor_brl=abs(valor),
                        motivo=f"Lançamento '{descricao}' não classificado por regras conhecidas. Encaminhado para decisão contábil.",
                        quem_decide="Helena / Contabilidade",
                    )
                )

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

    # 3. BANCO MERIDIANO (C/C 90233-5)
    for row in meridiano_rows:
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
        elif re.search(r"REPASSE COMISSAO \d{2}/\d{4}", desc_upper):
            conta_codigo = "1.1.03.002"
        elif "MESMA TITULARIDADE" in desc_upper:
            conta_codigo = "1.1.09.001"
        else:
            metodo = "HUMANO"
            confianca = Decimal("0.00")
            conta_codigo = "1.1.09.002"
            pendencias.append(
                LinhaPendenciaContabil(
                    tipo="LANCAMENTO_SEM_REGRA",
                    ref_origem=ref_origem,
                    valor_brl=abs(valor),
                    motivo=f"Lançamento '{descricao}' não classificado por regras conhecidas. Encaminhado para decisão contábil.",
                    quem_decide="Helena / Contabilidade",
                )
            )

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
