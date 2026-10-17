"""
Motor de Checkout e Divergências de Taxa (Camada Gold).
Processa o lote principal (01) e o lote incremental de ajustes tardios (06).
"""

from __future__ import annotations
import csv
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from ..utils import round_half_up


@dataclass
class LinhaComissaoLojista:
    cnpj: str
    lojista: str
    linha_negocio: str  # 'CHECKOUT'
    comissao_brl: Decimal
    transacoes_count: int = 0
    id_saida: str = ""


@dataclass
class LinhaDivergenciaTaxa:
    cnpj: str
    linha_negocio: str  # 'CHECKOUT'
    ref_origem: str     # id_transacao
    taxa_contratada_pct: Decimal
    taxa_aplicada_pct: Decimal
    diferenca_brl: Decimal
    id_saida: str = ""


@dataclass
class LinhaPendencia:
    tipo: str
    ref_origem: str
    valor_brl: Decimal
    motivo: str
    quem_decide: str
    cnpj: str = ""
    id_saida: str = ""


@dataclass
class LinhaRastro:
    id_saida: str
    arquivo_origem: str
    ref_origem: str
    valor: Decimal
    regra_aplicada: str = ""
    taxa_contratada_aplicada: str = ""
    detalhe_calculo: str = ""


@dataclass
class ResultadoCheckout:
    comissoes: List[LinhaComissaoLojista]
    divergencias: List[LinhaDivergenciaTaxa]
    pendencias: List[LinhaPendencia]
    rastro: List[LinhaRastro]
    totais_por_lojista: Dict[str, Decimal] = field(default_factory=dict)


def _normalizar_pct(val_str: str) -> Decimal:
    if not val_str or not val_str.strip():
        return Decimal("0.00")
    s = val_str.strip().rstrip("%").lower()
    if s in ("padrão", "padrao"):
        return Decimal("0.015")
    try:
        d = Decimal(s)
        if d >= Decimal("0.20"):
            return d / Decimal("100")
        return d
    except Exception:
        return Decimal("0.00")


def carregar_contratos(tabela_taxas_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    contratos_por_ec: Dict[str, List[Dict[str, Any]]] = {}
    with open(tabela_taxas_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            ec = row.get("ec_orbe", "").strip()
            cnpj = row.get("cnpj", "").strip()
            lojista = row.get("lojista", "").strip()
            vigencia = row.get("vigencia", "").strip()

            c_info = {
                "lojista": lojista,
                "cnpj": cnpj,
                "ec_orbe": ec,
                "vigencia": vigencia,
                "debito": _normalizar_pct(row.get("debito", "")),
                "credito_a_vista": _normalizar_pct(row.get("credito_a_vista", "")),
                "cred_2_6x": _normalizar_pct(row.get("cred_2_6x", "")),
                "cred_7_12x": _normalizar_pct(row.get("cred_7_12x", "")),
                "pix": _normalizar_pct(row.get("pix", "")),
                "antecipacao": _normalizar_pct(row.get("antecipacao", "")),
                "spread_remessa": _normalizar_pct(row.get("spread_remessa", "")),
                "obs": row.get("obs", ""),
            }
            if ec:
                contratos_por_ec.setdefault(ec, []).append(c_info)

    # Adiciona os 3 mapeamentos conhecidos confirmados no Slack pela Helena (Dúvida 5)
    # 1043300981 -> Novo Horizonte Intercambio
    # 1043396662 -> Horizonte Viagens
    # 1038867654 -> Kiwi Experience
    with open(tabela_taxas_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            cnpj = row.get("cnpj", "").strip()
            for ec_target, cnpj_target in [
                ("1043300981", "66564512000199"),
                ("1043396662", "78576234000179"),
                ("1038867654", "07752116000126"),
            ]:
                if cnpj == cnpj_target:
                    contratos_por_ec.setdefault(ec_target, []).append({
                        "lojista": row.get("lojista", "").strip(),
                        "cnpj": cnpj,
                        "ec_orbe": ec_target,
                        "vigencia": row.get("vigencia", "").strip(),
                        "debito": _normalizar_pct(row.get("debito", "")),
                        "credito_a_vista": _normalizar_pct(row.get("credito_a_vista", "")),
                        "cred_2_6x": _normalizar_pct(row.get("cred_2_6x", "")),
                        "cred_7_12x": _normalizar_pct(row.get("cred_7_12x", "")),
                        "pix": _normalizar_pct(row.get("pix", "")),
                        "antecipacao": _normalizar_pct(row.get("antecipacao", "")),
                        "spread_remessa": _normalizar_pct(row.get("spread_remessa", "")),
                        "obs": row.get("obs", ""),
                    })

    return contratos_por_ec


def obter_taxa_contratada(
    contratos: List[Dict[str, Any]],
    data_operacao: str,
    tipo_lancamento: int,
    modalidade: int,
    qtd_parcelas: int,
) -> Tuple[Decimal, str, str]:
    contrato_escolhido = contratos[0]
    if len(contratos) > 1:
        for c in contratos:
            vig = c["vigencia"]
            if vig.endswith("-ate"):
                if data_operacao <= vig.replace("-ate", ""):
                    contrato_escolhido = c
                    break
            elif vig.endswith("-apd"):
                if data_operacao >= vig.replace("-apd", ""):
                    contrato_escolhido = c
                    break

    cnpj = contrato_escolhido["cnpj"]
    lojista = contrato_escolhido["lojista"]

    if tipo_lancamento in (3, 4):  # Antecipação ou Reversão de Antecipação
        return contrato_escolhido["antecipacao"], cnpj, lojista

    if modalidade == 4:  # Débito
        return contrato_escolhido["debito"], cnpj, lojista
    elif modalidade == 3:  # PIX
        return contrato_escolhido["pix"], cnpj, lojista
    elif modalidade == 1:  # Crédito à vista
        return contrato_escolhido["credito_a_vista"], cnpj, lojista
    elif modalidade == 2:  # Crédito Parcelado
        if qtd_parcelas <= 6:
            return contrato_escolhido["cred_2_6x"], cnpj, lojista
        else:
            return contrato_escolhido["cred_7_12x"], cnpj, lojista

    return Decimal("0.00"), cnpj, lojista


def processar_checkout(
    orbe_csv_paths: List[Path],
    tabela_taxas_path: Path,
) -> ResultadoCheckout:
    contratos_map = carregar_contratos(tabela_taxas_path)

    MAPA_BANDEIRAS = {0: "OUTROS", 1: "MASTERCARD", 2: "ELO", 3: "VISA", 4: "AMEX", 5: "HIPERCARD"}
    MAPA_MODALIDADES = {0: "Operação", 1: "Crédito à vista", 2: "Crédito parcelado", 3: "PIX", 4: "Débito"}

    comissoes_acumuladas: Dict[str, Dict[str, Any]] = {}
    divergencias: List[LinhaDivergenciaTaxa] = []
    pendencias: List[LinhaPendencia] = []
    rastro: List[LinhaRastro] = []

    rows: List[Tuple[Dict[str, str], str]] = []
    tx_primarias: Dict[str, Dict[str, str]] = {}

    for p in orbe_csv_paths:
        if p.exists():
            with open(p, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=";")
                for r in reader:
                    rows.append((r, p.name))
                    if "01" in p.name or "principal" in p.name:
                        tx_primarias[r["id_transacao"].strip()] = r

    tx_vistas: Dict[str, Dict[str, Any]] = {}
    casa_isencao_txs: List[Tuple[str, Decimal]] = []

    for row, arq_origem in rows:
        id_transacao = row["id_transacao"].strip()
        data_mov = row["data_movimento"].strip()
        ec = row["cod_estabelecimento"].strip()
        nome_estab = row["nome_estabelecimento"].strip()
        tipo_lancto = int(row["tipo_lancamento"])
        modalidade = int(row["modalidade"]) if row["modalidade"] else 0
        qtd_parcelas = int(row["qtd_parcelas"]) if row["qtd_parcelas"] else 1
        valor_bruto = Decimal(row["valor_bruto"])
        taxa_aplicada_pct = Decimal(row["taxa_aplicada_pct"]) if row["taxa_aplicada_pct"] else Decimal("0.00")
        valor_taxa_str = row.get("valor_taxa", "").strip()
        valor_taxa = Decimal(valor_taxa_str) if valor_taxa_str else round_half_up(valor_bruto * (taxa_aplicada_pct / Decimal("100")))
        data_venda_orig = row.get("data_venda_original", "").strip()
        id_referencia = row.get("id_referencia", "").strip()

        # Deduplicação inteligente e bloqueio de duplicidades conflitantes (Prioridade 4)
        if id_transacao in tx_vistas:
            tx_antiga = tx_vistas[id_transacao]
            mesmos_valores = (
                tx_antiga["valor_bruto"] == valor_bruto
                and tx_antiga["tipo_lancto"] == tipo_lancto
                and tx_antiga["ec"] == ec
            )
            if mesmos_valores:
                continue
            else:
                pendencias.append(
                    LinhaPendencia(
                        tipo="DUPLICIDADE_CONFLITANTE",
                        ref_origem=id_transacao,
                        valor_brl=round_half_up(valor_taxa),
                        motivo=(
                            f"Transação {id_transacao} encontrada com dados conflitantes entre fontes "
                            f"(Anterior: R$ {tx_antiga['valor_bruto']}, Novo: R$ {valor_bruto}). Bloqueada para auditoria."
                        ),
                        quem_decide="Helena / Conciliação",
                    )
                )
                continue

        tx_vistas[id_transacao] = {
            "valor_bruto": valor_bruto,
            "tipo_lancto": tipo_lancto,
            "ec": ec,
            "data_mov": data_mov,
        }

        # Nome de arquivo amigável canônico
        arq_amigavel = (
            "01_orbe_relatorio_comissoes_set2026.csv"
            if ("01" in arq_origem or "principal" in arq_origem)
            else (
                "06_orbe_ajustes_tardios_set2026.csv"
                if ("06" in arq_origem or "tardio" in arq_origem)
                else arq_origem
            )
        )

        # REGRA 1: ATLAS IDIOMAS (1076801732) - BLOQUEIO TOTAL
        # Valor da pendência representa a taxa/comissão em disputa (não inflar com bruto)
        if ec == "1076801732":
            pendencias.append(
                LinhaPendencia(
                    tipo="CADASTRO_PENDENTE",
                    ref_origem=id_transacao,
                    valor_brl=round_half_up(valor_taxa),
                    motivo=f"Atlas Idiomas iniciou em 10/09 sem contrato assinado vigente (bruto R$ {valor_bruto:.2f}, taxa em disputa R$ {valor_taxa:.2f}). Não faturar até confirmação do Comercial.",
                    quem_decide="Bia / Comercial",
                    cnpj="39566044000119",
                )
            )
            continue

        # Identifica contrato cadastrado para o EC
        contratos = contratos_map.get(ec)
        if not contratos:
            pendencias.append(
                LinhaPendencia(
                    tipo="EC_NAO_CONTRATADO",
                    ref_origem=id_transacao,
                    valor_brl=round_half_up(valor_taxa),
                    motivo=f"EC {ec} ({nome_estab}) não possui contrato cadastrado.",
                    quem_decide="Bia / Comercial",
                )
            )
            continue

        cnpj_default = contratos[0]["cnpj"]

        # REGRA 2: CASA DO ESTUDANTE (1018325654) - ISENÇÃO SET-DEZ/2026
        if ec == "1018325654":
            if "2026-09-01" <= data_mov <= "2026-12-31":
                if tipo_lancto == 2 and data_venda_orig and data_venda_orig < "2026-09-01":
                    taxa_contratada_prop, cnpj, lojista = obter_taxa_contratada(
                        contratos, data_venda_orig, tipo_lancto, modalidade, qtd_parcelas
                    )
                    taxa_contratada_pct = taxa_contratada_prop * Decimal("100")
                    comissao_linha = round_half_up(valor_bruto * taxa_contratada_prop)
                    regra_aplicada = f"Estorno anterior a set/2026 pela taxa da venda original ({data_venda_orig}) (Regra Helena)"
                    taxa_contratada_str = f"{taxa_contratada_pct:.2f}%"
                    detalhe_calc = f"Bruto R$ {valor_bruto:.2f} * {taxa_contratada_pct:.2f}% = R$ {comissao_linha:.2f}"

                    if cnpj not in comissoes_acumuladas:
                        comissoes_acumuladas[cnpj] = {"cnpj": cnpj, "lojista": lojista, "total": Decimal("0.00"), "count": 0, "refs": []}
                    comissoes_acumuladas[cnpj]["total"] += comissao_linha
                    comissoes_acumuladas[cnpj]["count"] += 1
                    comissoes_acumuladas[cnpj]["refs"].append((id_transacao, comissao_linha, arq_amigavel, regra_aplicada, taxa_contratada_str, detalhe_calc))
                else:
                    casa_isencao_txs.append((id_transacao, valor_taxa))
                continue

        # Obtenção da taxa contratual aplicável
        data_para_taxa = data_venda_orig if (tipo_lancto in (2, 4) and data_venda_orig) else data_mov
        if not data_para_taxa and id_referencia and id_referencia in tx_primarias:
            data_para_taxa = tx_primarias[id_referencia].get("data_movimento", data_mov)

        taxa_contratada_prop, cnpj, lojista = obter_taxa_contratada(
            contratos, data_para_taxa, tipo_lancto, modalidade, qtd_parcelas
        )

        taxa_contratada_pct = taxa_contratada_prop * Decimal("100")
        comissao_linha = round_half_up(valor_bruto * taxa_contratada_prop)

        # Regra textual explicativa para auditoria
        if tipo_lancto == 1:
            mod_str = MAPA_MODALIDADES.get(modalidade, "Venda")
            if modalidade == 2:
                mod_str += f" ({qtd_parcelas}x)"
            regra_aplicada = f"Taxa contratual {mod_str}"
            if ec == "1075624862":  # Bridge Idiomas vigência 15/09
                regra_aplicada += f" (Corte vigência {'pós-15/09' if data_mov >= '2026-09-15' else 'pré-15/09'})"
        elif tipo_lancto == 2:
            regra_aplicada = f"Estorno à taxa da venda original ({data_para_taxa})"
        elif tipo_lancto == 3:
            regra_aplicada = "Taxa contratual de antecipação"
        elif tipo_lancto == 4:
            regra_aplicada = f"Reversão de antecipação à taxa da antecipação original ({data_para_taxa})"
        else:
            regra_aplicada = "Operação comercial padrão"

        taxa_contratada_str = f"{taxa_contratada_pct:.2f}%"
        detalhe_calc = f"Bruto R$ {valor_bruto:.2f} * {taxa_contratada_pct:.2f}% = R$ {comissao_linha:.2f}"

        # AUDITORIA DE AJUSTES TARDIOS (ARQUIVO 06)
        if "06" in arq_origem or "tardio" in arq_origem:
            if id_referencia:
                if id_referencia in tx_primarias:
                    # Auditoria de Divergência Cadastral de Bandeira (Confirmação 17/10 - Homologado por Helena)
                    if tipo_lancto == 2:
                        tx_orig = tx_primarias[id_referencia]
                        b_v = int(tx_orig.get("bandeira", "0") or "0")
                        b_e = int(row.get("bandeira", "0") or "0")
                        if b_v != b_e:
                            b_v_nome = MAPA_BANDEIRAS.get(b_v, str(b_v))
                            b_e_nome = MAPA_BANDEIRAS.get(b_e, str(b_e))
                            # Conforme homologado por Helena: "Bandeira não muda a taxa... não precisa contestar nem abrir pendência"
                            # Preserva evidência documental sem gerar pendência indevida
                            detalhe_calc += f" [Estorno bandeira {b_e_nome} vs venda {b_v_nome} - vínculo por referência homologado por Helena]"
                else:
                    # Regra Helena 14h10: Estorno Órfão entra pelo valor declarado e vira pendência
                    if tipo_lancto in (2, 4):
                        pendencias.append(
                            LinhaPendencia(
                                tipo="ESTORNO_ORFAO_SEM_ORIGEM",
                                ref_origem=id_transacao,
                                valor_brl=round_half_up(valor_bruto),
                                motivo=(
                                    f"Ajuste tardio {id_transacao} referencia transação original {id_referencia} ausente do relatório principal. "
                                    f"Incluído na apuração pelo valor declarado; pendente solicitação da transação original à Orbe."
                                ),
                                quem_decide="Helena",
                                cnpj=cnpj,
                            )
                        )

        if cnpj not in comissoes_acumuladas:
            comissoes_acumuladas[cnpj] = {"cnpj": cnpj, "lojista": lojista, "total": Decimal("0.00"), "count": 0, "refs": []}

        comissoes_acumuladas[cnpj]["total"] += comissao_linha
        comissoes_acumuladas[cnpj]["count"] += 1
        comissoes_acumuladas[cnpj]["refs"].append((id_transacao, comissao_linha, arq_amigavel, regra_aplicada, taxa_contratada_str, detalhe_calc))

        # Divergência de Taxa (Tolerância descartada; apenas se taxa aplicada != contratada)
        diff_taxa_pct = taxa_aplicada_pct - taxa_contratada_pct
        if abs(diff_taxa_pct) >= Decimal("0.005"):
            diferenca_brl = round_half_up(valor_bruto * (diff_taxa_pct / Decimal("100")))
            divergencias.append(
                LinhaDivergenciaTaxa(
                    cnpj=cnpj,
                    linha_negocio="CHECKOUT",
                    ref_origem=id_transacao,
                    taxa_contratada_pct=taxa_contratada_pct.quantize(Decimal("0.01")),
                    taxa_aplicada_pct=taxa_aplicada_pct.quantize(Decimal("0.01")),
                    diferenca_brl=diferenca_brl,
                )
            )
    # Consolidação da isenção da Casa do Estudante (elimina ruído de 118 pendências e apura taxa exata em jogo)
    if casa_isencao_txs:
        total_taxa_casa = sum(v for _, v in casa_isencao_txs)
        pendencias.append(
            LinhaPendencia(
                tipo="ISENCAO_NAO_AVISADA",
                ref_origem=f"LOTE_ISENCAO_{len(casa_isencao_txs)}_TX",
                valor_brl=round_half_up(total_taxa_casa),
                motivo=(
                    f"Casa do Estudante (1018325654): Isenção total de MDR/Antecipação no período set-dez/2026 (taxa 0.00%) "
                    f"não comunicada à Orbe. Lote consolidado de {len(casa_isencao_txs)} transações com taxa indevida de R$ {total_taxa_casa:.2f} "
                    f"a ser devolvida ao lojista via negociação comercial."
                ),
                quem_decide="Helena / Comercial",
                cnpj="00520815000100",
            )
        )

    lista_comissoes: List[LinhaComissaoLojista] = []
    totais_map: Dict[str, Decimal] = {}

    for cnpj, dados in sorted(comissoes_acumuladas.items(), key=lambda x: x[1]["lojista"]):
        total_comissao = round_half_up(dados["total"])
        totais_map[cnpj] = total_comissao
        lista_comissoes.append(
            LinhaComissaoLojista(
                cnpj=cnpj,
                lojista=dados["lojista"],
                linha_negocio="CHECKOUT",
                comissao_brl=total_comissao,
                transacoes_count=dados["count"],
            )
        )
        for ref, v_linha, arq, regra, tx_str, det_calc in dados["refs"]:
            rastro.append(
                LinhaRastro(
                    id_saida=cnpj,
                    arquivo_origem=arq,
                    ref_origem=ref,
                    valor=v_linha,
                    regra_aplicada=regra,
                    taxa_contratada_aplicada=tx_str,
                    detalhe_calculo=det_calc,
                )
            )

    return ResultadoCheckout(
        comissoes=lista_comissoes,
        divergencias=divergencias,
        pendencias=pendencias,
        rastro=rastro,
        totais_por_lojista=totais_map,
    )
