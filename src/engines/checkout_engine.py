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
    arquivo_origem: str = "01_orbe_relatorio_comissoes_set2026.csv"


@dataclass
class LinhaPendencia:
    tipo: str
    ref_origem: str
    valor_brl: Decimal
    motivo: str
    quem_decide: str
    cnpj: str = ""
    id_saida: str = ""
    arquivo_origem: str = ""
    rastro_itens: List[LinhaRastro] = field(default_factory=list)


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


def _nome_arq_orbe_amigavel(arq_origem: str) -> str:
    low = arq_origem.lower()
    if "01" in low or "principal" in low:
        return "01_orbe_relatorio_comissoes_set2026.csv"
    if "06" in low or "tardio" in low:
        return "06_orbe_ajustes_tardios_set2026.csv"
    return arq_origem


def _assinatura_transacao_orbe(row: Dict[str, str]) -> Tuple[Any, ...]:
    """Retorna tupla canônica com todos os campos relevantes para comparação de duplicidade."""
    ec = row.get("cod_estabelecimento", "").strip()
    tipo_lancto = int(row.get("tipo_lancamento") or 0)
    modalidade = int(row.get("modalidade") or 0)
    qtd_parcelas = int(row.get("qtd_parcelas") or 1)
    bandeira = int(row.get("bandeira") or 0)
    valor_bruto = Decimal(row.get("valor_bruto") or "0.00")
    taxa_aplicada_pct = Decimal(row.get("taxa_aplicada_pct") or "0.00")
    valor_taxa_str = row.get("valor_taxa", "").strip()
    valor_taxa = (
        Decimal(valor_taxa_str)
        if valor_taxa_str
        else round_half_up(valor_bruto * (taxa_aplicada_pct / Decimal("100")))
    )
    valor_liquido_str = row.get("valor_liquido", "").strip()
    valor_liquido = Decimal(valor_liquido_str) if valor_liquido_str else (valor_bruto - valor_taxa)
    data_mov = row.get("data_movimento", "").strip()
    data_venda_orig = row.get("data_venda_original", "").strip()
    id_referencia = row.get("id_referencia", "").strip()
    return (
        ec,
        tipo_lancto,
        modalidade,
        qtd_parcelas,
        bandeira,
        round_half_up(valor_bruto),
        round_half_up(taxa_aplicada_pct),
        round_half_up(valor_taxa),
        round_half_up(valor_liquido),
        data_mov,
        data_venda_orig,
        id_referencia,
    )


def processar_checkout(
    orbe_csv_paths: List[Path],
    tabela_taxas_path: Path,
    competencia: Optional[str] = None,
) -> ResultadoCheckout:
    contratos_map = carregar_contratos(tabela_taxas_path)

    MAPA_BANDEIRAS = {0: "OUTROS", 1: "MASTERCARD", 2: "ELO", 3: "VISA", 4: "AMEX", 5: "HIPERCARD"}
    MAPA_MODALIDADES = {0: "Operação", 1: "Crédito à vista", 2: "Crédito parcelado", 3: "PIX", 4: "Débito"}

    comissoes_acumuladas: Dict[str, Dict[str, Any]] = {}
    divergencias: List[LinhaDivergenciaTaxa] = []
    pendencias: List[LinhaPendencia] = []
    rastro: List[LinhaRastro] = []

    rows_all: List[Tuple[Dict[str, str], str]] = []
    tx_primarias: Dict[str, Dict[str, str]] = {}

    for p in orbe_csv_paths:
        if p.exists():
            with open(p, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=";")
                for r in reader:
                    rows_all.append((r, p.name))

    # Pré-passo de agrupamento por id_transacao para detectar duplicatas exatas vs conflitantes
    # antes de acumular qualquer comissão ou divergência (evita First-Write-Wins).
    grupos_por_id: Dict[str, List[Tuple[Dict[str, str], str]]] = {}
    for r, arq_nome in rows_all:
        id_tx = r["id_transacao"].strip()
        grupos_por_id.setdefault(id_tx, []).append((r, arq_nome))

    ids_conflitantes: set[str] = set()
    evidencia_dedup_exata: Dict[str, str] = {}

    for id_tx, ocorrencias in grupos_por_id.items():
        if len(ocorrencias) == 1:
            r0, a0 = ocorrencias[0]
            tx_primarias[id_tx] = r0
            continue

        assinaturas = [_assinatura_transacao_orbe(r) for r, _ in ocorrencias]
        if len(set(assinaturas)) == 1:
            # Registro efetivamente idêntico em todos os campos relevantes: preserva 1ª ocorrência e registra evidência
            r0, _ = ocorrencias[0]
            tx_primarias[id_tx] = r0
            arqs_envolvidos = [_nome_arq_orbe_amigavel(a) for _, a in ocorrencias]
            evidencia_dedup_exata[id_tx] = (
                f" [Deduplicado: {len(ocorrencias)} ocorrências idênticas em {', '.join(arqs_envolvidos)}]"
            )
        else:
            # Conflito de valores para o mesmo id_transacao: bloqueia TODAS as ocorrências!
            ids_conflitantes.add(id_tx)

    casa_isencao_txs: List[Tuple[str, Decimal, str, Decimal, Decimal]] = []
    ids_ja_processados: set[str] = set()

    for row, arq_origem in rows_all:
        id_transacao = row["id_transacao"].strip()
        if id_transacao in ids_ja_processados:
            continue

        ocorrencias_tx = grupos_por_id[id_transacao]
        # Se a competência foi informada, verifica se a transação (ou alguma versão conflitante dela) pertence à competência
        if competencia:
            pertence_competencia = any(
                r_oc.get("data_movimento", "").strip().startswith(competencia)
                for r_oc, _ in ocorrencias_tx
            )
            if not pertence_competencia:
                ids_ja_processados.add(id_transacao)
                continue

        ids_ja_processados.add(id_transacao)

        # Tratamento de IDs conflitantes: bloqueia integralmente (nenhuma versão entra em comissões ou divergências)
        if id_transacao in ids_conflitantes:
            rastro_conflito: List[LinhaRastro] = []
            descricoes_versoes: List[str] = []
            ec_first = ocorrencias_tx[0][0].get("cod_estabelecimento", "").strip()
            contratos_c = contratos_map.get(ec_first)
            cnpj_c = contratos_c[0]["cnpj"] if contratos_c else ("39566044000119" if ec_first == "1076801732" else "")

            for idx_oc, (r_oc, arq_oc) in enumerate(ocorrencias_tx, start=1):
                vb_oc = Decimal(r_oc.get("valor_bruto") or "0.00")
                tp_oc = Decimal(r_oc.get("taxa_aplicada_pct") or "0.00")
                vt_str = r_oc.get("valor_taxa", "").strip()
                vt_oc = round_half_up(
                    Decimal(vt_str) if vt_str else (vb_oc * (tp_oc / Decimal("100")))
                )
                arq_amig_oc = _nome_arq_orbe_amigavel(arq_oc)
                dm_oc = r_oc.get("data_movimento", "").strip()
                tl_oc = r_oc.get("tipo_lancamento", "").strip()
                descricoes_versoes.append(
                    f"v{idx_oc} ({arq_amig_oc}, data={dm_oc}, tipo={tl_oc}, bruto=R$ {vb_oc:.2f}, taxa={tp_oc:.2f}%, valor_taxa=R$ {vt_oc:.2f})"
                )
                rastro_conflito.append(
                    LinhaRastro(
                        id_saida="",
                        arquivo_origem=arq_amig_oc,
                        ref_origem=id_transacao,
                        valor=abs(vt_oc),
                        regra_aplicada="Bloqueio integral por duplicidade conflitante de id_transacao",
                        taxa_contratada_aplicada="BLOQUEADO",
                        detalhe_calculo=f"Versão {idx_oc} conflitante: bruto R$ {vb_oc:.2f}, taxa {tp_oc:.2f}%, valor_taxa R$ {vt_oc:.2f}",
                    )
                )

            valor_bloqueado = round_half_up(sum(item.valor for item in rastro_conflito))
            pendencias.append(
                LinhaPendencia(
                    tipo="DUPLICIDADE_CONFLITANTE",
                    ref_origem=id_transacao,
                    valor_brl=valor_bloqueado,
                    motivo=(
                        f"Transação {id_transacao} encontrada com dados conflitantes em {len(ocorrencias_tx)} registros "
                        f"[{'; '.join(descricoes_versoes)}]. Todas as ocorrências foram bloqueadas sem escolha automática."
                    ),
                    quem_decide="Helena / Conciliação",
                    cnpj=cnpj_c,
                    arquivo_origem=_nome_arq_orbe_amigavel(ocorrencias_tx[0][1]),
                    rastro_itens=rastro_conflito,
                )
            )
            continue

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

        arq_amigavel = _nome_arq_orbe_amigavel(arq_origem)
        sufixo_dedup = evidencia_dedup_exata.get(id_transacao, "")

        # REGRA 1: ATLAS IDIOMAS (1076801732) - BLOQUEIO TOTAL
        # Valor da pendência representa a taxa/comissão em disputa (não inflar com bruto)
        if ec == "1076801732":
            val_atlas = round_half_up(valor_taxa)
            pendencias.append(
                LinhaPendencia(
                    tipo="CADASTRO_PENDENTE",
                    ref_origem=id_transacao,
                    valor_brl=val_atlas,
                    motivo=f"Atlas Idiomas iniciou em 10/09 sem contrato assinado vigente (bruto R$ {valor_bruto:.2f}, taxa em disputa R$ {valor_taxa:.2f}). Não faturar até confirmação do Comercial.{sufixo_dedup}",
                    quem_decide="Bia / Comercial",
                    cnpj="39566044000119",
                    arquivo_origem=arq_amigavel,
                    rastro_itens=[
                        LinhaRastro(
                            id_saida="",
                            arquivo_origem=arq_amigavel,
                            ref_origem=id_transacao,
                            valor=val_atlas,
                            regra_aplicada="Bloqueio contratual Atlas Idiomas (EC sem contrato assinado)",
                            taxa_contratada_aplicada="PENDENTE",
                            detalhe_calculo=f"Bruto R$ {valor_bruto:.2f}, taxa cobrada {taxa_aplicada_pct:.2f}% = R$ {val_atlas:.2f}{sufixo_dedup}",
                        )
                    ],
                )
            )
            continue

        # Identifica contrato cadastrado para o EC
        contratos = contratos_map.get(ec)
        if not contratos:
            val_ec_nc = round_half_up(valor_taxa)
            pendencias.append(
                LinhaPendencia(
                    tipo="EC_NAO_CONTRATADO",
                    ref_origem=id_transacao,
                    valor_brl=val_ec_nc,
                    motivo=f"EC {ec} ({nome_estab}) não possui contrato cadastrado.{sufixo_dedup}",
                    quem_decide="Bia / Comercial",
                    arquivo_origem=arq_amigavel,
                    rastro_itens=[
                        LinhaRastro(
                            id_saida="",
                            arquivo_origem=arq_amigavel,
                            ref_origem=id_transacao,
                            valor=val_ec_nc,
                            regra_aplicada="Bloqueio de EC sem contrato na tabela de taxas",
                            taxa_contratada_aplicada="N/A",
                            detalhe_calculo=f"EC {ec} ({nome_estab}) bruto R$ {valor_bruto:.2f}, taxa R$ {val_ec_nc:.2f}{sufixo_dedup}",
                        )
                    ],
                )
            )
            continue

        # REGRA 2: CASA DO ESTUDANTE (1018325654) - ISENÇÃO SET-DEZ/2026
        if ec == "1018325654":
            data_orig_casa = data_venda_orig
            if not data_orig_casa and id_referencia and id_referencia in tx_primarias:
                data_orig_casa = tx_primarias[id_referencia].get("data_movimento", "").strip()
            if "2026-09-01" <= data_mov <= "2026-12-31":
                if tipo_lancto in (2, 4) and data_orig_casa and data_orig_casa < "2026-09-01":
                    taxa_contratada_prop, cnpj, lojista = obter_taxa_contratada(
                        contratos, data_orig_casa, tipo_lancto, modalidade, qtd_parcelas
                    )
                    taxa_contratada_pct = taxa_contratada_prop * Decimal("100")
                    comissao_linha = round_half_up(valor_bruto * taxa_contratada_prop)
                    regra_aplicada = f"Estorno anterior a set/2026 pela taxa da venda original ({data_orig_casa}) (Regra Helena)"
                    taxa_contratada_str = f"{taxa_contratada_pct:.2f}%"
                    detalhe_calc = f"Bruto R$ {valor_bruto:.2f} * {taxa_contratada_pct:.2f}% = R$ {comissao_linha:.2f}{sufixo_dedup}"

                    if cnpj not in comissoes_acumuladas:
                        comissoes_acumuladas[cnpj] = {"cnpj": cnpj, "lojista": lojista, "total": Decimal("0.00"), "count": 0, "refs": []}
                    comissoes_acumuladas[cnpj]["total"] += comissao_linha
                    comissoes_acumuladas[cnpj]["count"] += 1
                    comissoes_acumuladas[cnpj]["refs"].append((id_transacao, comissao_linha, arq_amigavel, regra_aplicada, taxa_contratada_str, detalhe_calc))
                else:
                    casa_isencao_txs.append(
                        (id_transacao, round_half_up(valor_taxa), arq_amigavel, valor_bruto, taxa_aplicada_pct)
                    )
                continue

        # Obtenção da taxa contratual aplicável preservando vigência histórica para estornos/reversões
        if tipo_lancto in (2, 4):
            if data_venda_orig:
                data_para_taxa = data_venda_orig
            elif id_referencia and id_referencia in tx_primarias:
                data_para_taxa = tx_primarias[id_referencia].get("data_movimento", "").strip() or data_mov
            else:
                data_para_taxa = data_mov
        else:
            data_para_taxa = data_mov

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
                regra_aplicada += f" (Corte vigência {'pós-15/09' if data_para_taxa >= '2026-09-15' else 'pré-15/09'})"
        elif tipo_lancto == 2:
            regra_aplicada = f"Estorno à taxa da venda original ({data_para_taxa})"
        elif tipo_lancto == 3:
            regra_aplicada = "Taxa contratual de antecipação"
        elif tipo_lancto == 4:
            regra_aplicada = f"Reversão de antecipação à taxa da antecipação original ({data_para_taxa})"
        else:
            regra_aplicada = "Operação comercial padrão"

        taxa_contratada_str = f"{taxa_contratada_pct:.2f}%"
        detalhe_calc = f"Bruto R$ {valor_bruto:.2f} * {taxa_contratada_pct:.2f}% = R$ {comissao_linha:.2f}{sufixo_dedup}"

        # AUDITORIA DE AJUSTES TARDIOS E REFERÊNCIAS HISTÓRICAS
        is_ajuste_file = ("06" in arq_origem or "tardio" in arq_origem or "ajuste" in arq_origem.lower())
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
                        detalhe_calc += f" [Estorno bandeira {b_e_nome} vs venda {b_v_nome} - vínculo por referência homologado por Helena]"
            elif is_ajuste_file and tipo_lancto in (2, 4):
                # Regra Helena 14h10: Estorno Órfão entra pelo valor declarado e vira pendência
                val_orfao = round_half_up(valor_bruto)
                pendencias.append(
                    LinhaPendencia(
                        tipo="ESTORNO_ORFAO_SEM_ORIGEM",
                        ref_origem=id_transacao,
                        valor_brl=val_orfao,
                        motivo=(
                            f"Ajuste tardio {id_transacao} referencia transação original {id_referencia} ausente do relatório principal. "
                            f"Incluído na apuração pelo valor declarado; pendente solicitação da transação original à Orbe."
                        ),
                        quem_decide="Helena",
                        cnpj=cnpj,
                        arquivo_origem=arq_amigavel,
                        rastro_itens=[
                            LinhaRastro(
                                id_saida="",
                                arquivo_origem=arq_amigavel,
                                ref_origem=id_transacao,
                                valor=val_orfao,
                                regra_aplicada="Estorno órfão sem transação original localizada (Regra Helena)",
                                taxa_contratada_aplicada=taxa_contratada_str,
                                detalhe_calculo=f"Referência original {id_referencia} ausente; valor bruto R$ {val_orfao:.2f}",
                            )
                        ],
                    )
                )

        if cnpj not in comissoes_acumuladas:
            comissoes_acumuladas[cnpj] = {"cnpj": cnpj, "lojista": lojista, "total": Decimal("0.00"), "count": 0, "refs": []}

        comissoes_acumuladas[cnpj]["total"] += comissao_linha
        comissoes_acumuladas[cnpj]["count"] += 1
        comissoes_acumuladas[cnpj]["refs"].append((id_transacao, comissao_linha, arq_amigavel, regra_aplicada, taxa_contratada_str, detalhe_calc))

        # Divergência de Taxa (apenas se taxa aplicada != contratada)
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
                    arquivo_origem=arq_amigavel,
                )
            )

    # Consolidação da isenção da Casa do Estudante preservando as 118 contribuições reais da Orbe no rastro
    if casa_isencao_txs:
        rastro_casa = [
            LinhaRastro(
                id_saida="",
                arquivo_origem=arq_c,
                ref_origem=id_tx_c,
                valor=val_tx_c,
                regra_aplicada="Isenção contratual set-dez/2026 (0.00%) não aplicada pela Orbe",
                taxa_contratada_aplicada="0.00%",
                detalhe_calculo=f"Bruto R$ {v_bruto_c:.2f} cobrado a {tx_ap_c:.2f}% = Taxa indevida R$ {val_tx_c:.2f}",
            )
            for id_tx_c, val_tx_c, arq_c, v_bruto_c, tx_ap_c in casa_isencao_txs
        ]
        total_taxa_casa = sum(item.valor for item in rastro_casa)
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
                arquivo_origem=casa_isencao_txs[0][2],
                rastro_itens=rastro_casa,
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

