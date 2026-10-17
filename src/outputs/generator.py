"""
Emissor Atômico das Saídas Oficiais e Prova Real do Rastro (Camada Gold).
Gera simultaneamente em 'fechamento-completo/' e no diretório oficial 'saida/'.
Implementa o Padrão Ouro de Auditabilidade da Organização Barte (14h11).
"""

from __future__ import annotations
import csv
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from ..engines.checkout_engine import ResultadoCheckout
from ..engines.cambio_engine import ResultadoRemessas
from ..engines.banking_engine import ResultadoContabil
from ..utils import VERSAO_REGRAS, sha256_file, format_competencia_br
from .execution_store import preparar_execucao, finalizar_execucao


def validar_prova_real(
    comissoes_rows: List[Dict[str, str]],
    notas_rows: List[Dict[str, str]],
    divergencias_rows: List[Dict[str, str]],
    lancamentos_rows: List[Dict[str, str]],
    pendencias_rows: List[Dict[str, str]],
    rastro_rows: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Verifica matematicamente que a soma do rastro por id_saida bate 100% com o valor reportado."""
    somas_rastro: Dict[str, Decimal] = {}
    for r in rastro_rows:
        s_id = r["id_saida"]
        val = Decimal(r["valor"])
        somas_rastro[s_id] = somas_rastro.get(s_id, Decimal("0.00")) + val

    erros: List[str] = []

    # 1. Comissões
    for c in comissoes_rows:
        sid = c["id_saida"]
        esp = Decimal(c["comissao_brl"])
        obt = somas_rastro.get(sid, Decimal("0.00"))
        if abs(esp - obt) > Decimal("0.001"):
            erros.append(f"COM {sid} ({c['lojista']}): esperado {esp:.2f}, rastro somou {obt:.2f}")

    # 2. Notas Fiscais
    for n in notas_rows:
        sid = n["id_saida"]
        esp = Decimal(n["valor_brl"])
        obt = somas_rastro.get(sid, Decimal("0.00"))
        if abs(esp - obt) > Decimal("0.001"):
            erros.append(f"NF {sid} ({n['tomador']}): esperado {esp:.2f}, rastro somou {obt:.2f}")

    # 3. Divergências de Taxa
    for d in divergencias_rows:
        sid = d["id_saida"]
        esp = Decimal(d["diferenca_brl"])
        obt = somas_rastro.get(sid, Decimal("0.00"))
        if abs(esp - obt) > Decimal("0.001"):
            erros.append(f"DIV {sid} ({d['ref_origem']}): esperado {esp:.2f}, rastro somou {obt:.2f}")

    # 4. Lançamentos Classificados
    for l in lancamentos_rows:
        sid = l["id_saida"]
        esp = Decimal(l["valor"])
        obt = somas_rastro.get(sid, Decimal("0.00"))
        if abs(esp - obt) > Decimal("0.001"):
            erros.append(f"LAN {sid} ({l['ref_origem']}): esperado {esp:.2f}, rastro somou {obt:.2f}")

    # 5. Pendências Operacionais
    for p in pendencias_rows:
        sid = p["id_saida"]
        esp = Decimal(p["valor_brl"])
        obt = somas_rastro.get(sid, Decimal("0.00"))
        if abs(esp - obt) > Decimal("0.001"):
            erros.append(f"PEN {sid} ({p['ref_origem']}): esperado {esp:.2f}, rastro somou {obt:.2f}")

    total_validados = (
        len(comissoes_rows)
        + len(notas_rows)
        + len(divergencias_rows)
        + len(lancamentos_rows)
        + len(pendencias_rows)
    )

    return {
        "valido": len(erros) == 0,
        "erros": erros,
        "total_ids_validados": total_validados,
    }


def _combinar_hashes(pares: List[Tuple[str, str]]) -> str:
    h = hashlib.sha256()
    for nome, digest in sorted(pares):
        h.update(f"{nome}:{digest}\n".encode("utf-8"))
    return h.hexdigest()


def gerar_manifestos_auditoria(
    state: Optional[Dict[str, Any]],
    comissoes_rows: List[Dict[str, str]],
    divergencias_rows: List[Dict[str, str]],
    notas_rows: List[Dict[str, str]],
    lancamentos_rows: List[Dict[str, str]],
    pendencias_rows: List[Dict[str, str]],
    rastro_rows: List[Dict[str, str]],
    prova_real: Dict[str, Any],
    output_dirs: List[Path],
) -> Dict[str, Any]:
    """Gera o registro completo de execução em JSON e Markdown com hashes, cobertura e diff entre execuções."""
    now_iso = datetime.now().astimezone().isoformat()
    status_solicitado = state.get("status_aprovacao", "PROVISORIO") if state else "PROVISORIO"
    competencia = state.get("competencia", "2026-09") if state else "2026-09"
    versao_regras = (state.get("versao_regras") if state else None) or VERSAO_REGRAS
    cobertura_fontes = (state.get("cobertura_fontes") if state else None) or {}
    estado_tecnico = (state.get("estado_tecnico") if state else None) or (
        "CONCLUIDO" if prova_real["valido"] else "PARCIAL_COM_BLOQUEIOS"
    )

    # 1. Lê manifesto anterior (se existir) ANTES de sobrescrever para rastrear diferenças e governança de aprovação
    manifesto_anterior: Optional[Dict[str, Any]] = state.get("manifesto_anterior") if state else None
    for d in output_dirs:
        if manifesto_anterior is not None:
            break
        cand_prev = d / "auditoria_execucao.json"
        if cand_prev.exists():
            try:
                with open(cand_prev, "r", encoding="utf-8") as fp:
                    loaded = json.load(fp)
                    if loaded.get("competencia") == competencia:
                        manifesto_anterior = loaded
                        break
            except Exception:
                pass

    # 2. Inventário de arquivos de entrada com SHA-256
    arquivos_inventario = []
    pares_hash_in: List[Tuple[str, str]] = []
    if state and "arquivos_descobertos" in state:
        for f in state["arquivos_descobertos"]:
            p = Path(f.get("caminho", ""))
            linhas_count = 0
            if p.exists() and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                        linhas_count = sum(1 for _ in fp)
                except Exception:
                    pass
            digest_in = sha256_file(p)
            nome_arq = f.get("nome", p.name)
            dom_arq = f.get("domain", "")
            cob_info = cobertura_fontes.get(dom_arq, {})
            pares_hash_in.append((nome_arq, digest_in))
            arquivos_inventario.append({
                "arquivo": nome_arq,
                "caminho": str(Path(state.get("data_dir_original", state["data_dir"])) / p.name),
                "copia_preservada": f"entradas/{p.name}",
                "dominio": dom_arq,
                "estado": cob_info.get("estado", f.get("status", "PROCESSADA")),
                "linhas_lidas": linhas_count,
                "tamanho_bytes": p.stat().st_size if p.exists() else 0,
                "sha256": digest_in,
                "metodo_triagem": f.get("triage_source", "HEURISTICA"),
            })

    hash_entradas_combinado = _combinar_hashes(pares_hash_in)

    # 3. Inventário de arquivos de saída com SHA-256
    ref_dir = output_dirs[0]
    nomes_saida = [
        ("comissoes_por_lojista.csv", len(comissoes_rows)),
        ("divergencias_taxa.csv", len(divergencias_rows)),
        ("notas_a_emitir.csv", len(notas_rows)),
        ("lancamentos_classificados.csv", len(lancamentos_rows)),
        ("pendencias.csv", len(pendencias_rows)),
        ("rastro.csv", len(rastro_rows)),
    ]
    arquivos_saida_inv = []
    pares_hash_out: List[Tuple[str, str]] = []
    for fname, qtd_reg in nomes_saida:
        f_out = ref_dir / fname
        digest_out = sha256_file(f_out)
        pares_hash_out.append((fname, digest_out))
        arquivos_saida_inv.append({
            "arquivo": fname,
            "registros": qtd_reg,
            "tamanho_bytes": f_out.stat().st_size if f_out.exists() else 0,
            "sha256": digest_out,
        })

    hash_saidas_combinado = _combinar_hashes(pares_hash_out)
    id_execucao = state["id_execucao"]

    total_comissao_brl = sum(Decimal(c["comissao_brl"]) for c in comissoes_rows)
    total_notas_brl = sum(Decimal(n["valor_brl"]) for n in notas_rows)
    total_divergencias_brl = sum(Decimal(d["diferenca_brl"]) for d in divergencias_rows)

    metricas_atuais = {
        "total_comissao_brl": f"{total_comissao_brl:.2f}",
        "total_notas_a_emitir_brl": f"{total_notas_brl:.2f}",
        "total_divergencias_taxa_brl": f"{total_divergencias_brl:.2f}",
        "qtd_comissoes": len(comissoes_rows),
        "qtd_notas": len(notas_rows),
        "qtd_divergencias": len(divergencias_rows),
        "qtd_lancamentos_contabeis": len(lancamentos_rows),
        "qtd_pendencias_operacionais": len(pendencias_rows),
        "qtd_linhas_rastro": len(rastro_rows),
    }

    # 4. Comparação entre execuções e separação entre estado_tecnico e status_aprovacao
    status_aprovacao_final = status_solicitado
    heranca_aprovacao_bloqueada = False

    if manifesto_anterior:
        prev_hash_in = manifesto_anterior.get("hash_entradas_combinado", "")
        prev_hash_out = manifesto_anterior.get("hash_saidas_combinado", "")
        prev_regras = manifesto_anterior.get("versao_regras", "")
        prev_status_aprov = manifesto_anterior.get(
            "status_aprovacao", manifesto_anterior.get("status_fechamento", "PROVISORIO")
        )
        entradas_identicas = (prev_hash_in == hash_entradas_combinado)
        saidas_identicas = (prev_hash_out == hash_saidas_combinado)
        regras_identicas = (prev_regras == versao_regras)
        codigo_identico = (
            manifesto_anterior.get("codigo_execucao", {}).get("sha256_fontes")
            == state["codigo_execucao"]["sha256_fontes"]
        )

        # Diferenças por métrica
        prev_metricas = manifesto_anterior.get("metricas_financeiras", {})
        diferencas_metricas: Dict[str, Dict[str, Any]] = {}
        for k, v_atual in metricas_atuais.items():
            v_ant = prev_metricas.get(k)
            if v_ant is not None and str(v_ant) != str(v_atual):
                diferencas_metricas[k] = {"anterior": v_ant, "atual": v_atual}

        # Diferenças por arquivo de saída
        prev_saidas_map = {
            item["arquivo"]: item.get("sha256", "")
            for item in manifesto_anterior.get("arquivos_saida", [])
        }
        arquivos_saida_alterados = [
            item["arquivo"]
            for item in arquivos_saida_inv
            if item["arquivo"] in prev_saidas_map and prev_saidas_map[item["arquivo"]] != item["sha256"]
        ]

        # Governança: resultados alterados não herdam aprovação anterior!
        if (not saidas_identicas or not entradas_identicas or not regras_identicas or not codigo_identico):
            if prev_status_aprov == "APROVADO_POR_HELENA" or status_solicitado == "APROVADO_POR_HELENA":
                status_aprovacao_final = "REABERTO_PARA_REVISAO"
                heranca_aprovacao_bloqueada = True

        comparacao_execucao = {
            "execucao_anterior_encontrada": True,
            "id_execucao_anterior": manifesto_anterior.get("id_execucao", "EXEC-ANTERIOR"),
            "versao_regras_anterior": prev_regras,
            "status_aprovacao_anterior": prev_status_aprov,
            "entradas_identicas": entradas_identicas,
            "saidas_identicas": saidas_identicas,
            "regras_identicas": regras_identicas,
            "codigo_identico": codigo_identico,
            "heranca_aprovacao_bloqueada": heranca_aprovacao_bloqueada,
            "diferencas_metricas": diferencas_metricas,
            "arquivos_saida_alterados": arquivos_saida_alterados,
        }
    else:
        comparacao_execucao = {
            "execucao_anterior_encontrada": False,
            "id_execucao_anterior": None,
            "entradas_identicas": None,
            "saidas_identicas": None,
            "regras_identicas": None,
            "codigo_identico": None,
            "heranca_aprovacao_bloqueada": False,
            "diferencas_metricas": {},
            "arquivos_saida_alterados": [],
        }

    if estado_tecnico != "CONCLUIDO" and status_aprovacao_final == "APROVADO_POR_HELENA":
        status_aprovacao_final = "REABERTO_PARA_REVISAO"
        comparacao_execucao["heranca_aprovacao_bloqueada"] = True

    if state is not None:
        state["id_execucao"] = id_execucao
        state["versao_regras"] = versao_regras
        state["estado_tecnico"] = estado_tecnico
        state["status_aprovacao"] = status_aprovacao_final
        state["comparacao_execucao_anterior"] = comparacao_execucao

    manifesto_data = {
        "manifesto_versao": "3.0.0",
        "id_execucao": id_execucao,
        "execucao_dir": state["execucao_dir"],
        "codigo_execucao": state["codigo_execucao"],
        "aprovacao_registro": "Status informado pelo operador; não autentica Helena.",
        "versao_regras": versao_regras,
        "data_hora_execucao": now_iso,
        "competencia": competencia,
        "estado_tecnico": estado_tecnico,
        "status_aprovacao": status_aprovacao_final,
        "status_fechamento": status_aprovacao_final,
        "prova_real_rastro_valida": prova_real["valido"],
        "total_ids_auditados": prova_real["total_ids_validados"],
        "erros_conciliacao": prova_real["erros"],
        "hash_entradas_combinado": hash_entradas_combinado,
        "hash_saidas_combinado": hash_saidas_combinado,
        "metricas_financeiras": metricas_atuais,
        "cobertura_fontes": cobertura_fontes,
        "indice_pendencias_cnpj": state.get("indice_pendencias_cnpj", {}),
        "arquivos_entrada": arquivos_inventario,
        "arquivos_saida": arquivos_saida_inv,
        "comparacao_execucao_anterior": comparacao_execucao,
        "regras_aplicadas_resumo": [
            "Checkout: Comissões apuradas pela taxa contratada por modalidade/parcelamento e filtradas por competência.",
            "Checkout: Bridge Idiomas (1075624862) split temporal de taxa em 15/09/2026 respeitando data da venda original em estornos.",
            "Checkout: Atlas Idiomas (1076801732) bloqueio total por ausência de contrato assinado (Bia/Comercial).",
            "Checkout: Casa do Estudante (1018325654) isenção set-dez consolidada em pendência com 118 transações reais no rastro.",
            "Checkout/Remessas: Deduplicação estrita de cópias idênticas e bloqueio integral de todas as versões em IDs conflitantes.",
            "Checkout: 7 divergências de bandeira no lote 06 vinculadas por referência sem abrir pendência indevida (homologado por Helena).",
            "Checkout: Estornos órfãos sem referência no relatório principal aceitos pelo valor declarado com pendência para Helena.",
            "Remessas: Split de 50% sobre o Spread BRL realizado (Ponte Câmbio).",
            "Remessas: Exclusão de 4 operações com spread negativo para contestação integral com a Ponte.",
            "Remessas: Deduplicação de PC-0926-0162 e contestação de spread contratual Mundo Aberto (1.20% vs 1.50%).",
            "Contábil: Classificação contábil com dupla conciliação bancária (Aurora CC 44710 e Meridiano CC 902335).",
        ],
    }

    # Gera Markdown executivo
    md_lines = [
        "# 📋 Manifesto de Auditoria da Execução — Fechamento Financeiro Tarvo",
        f"**ID da Execução:** `{id_execucao}`  ",
        f"**Versão de Regras:** `{versao_regras}`  ",
        f"**Competência:** `{competencia}` ({format_competencia_br(competencia)})  ",
        f"**Data e Hora:** {now_iso}  ",
        f"**Estado Técnico:** `{estado_tecnico}`  ",
        f"**Status de Aprovação Humana:** `{status_aprovacao_final}`  ",
        f"**Auditoria Matemática de Rastro:** `{'✅ 100% CONCILIADO' if prova_real['valido'] else '❌ DIVERGÊNCIAS DETECTADAS'}`  ",
        "",
        "---",
        "## 1. Cobertura e Estado das Fontes por Frente",
        "| Domínio | Frente | Estado | Arquivo | Motivo / Detalhe | Dependência | Responsável |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for dom_k, cob_v in cobertura_fontes.items():
        md_lines.append(
            f"| `{dom_k}` | {cob_v.get('frente', '')} | `{cob_v.get('estado', '')}` | "
            f"`{cob_v.get('arquivo', '-')}` | {cob_v.get('motivo', '')} | "
            f"{cob_v.get('dependencia', '')} | {cob_v.get('responsavel', '')} |"
        )

    md_lines.extend([
        "",
        "---",
        "## 2. Inventário de Arquivos de Entrada (SHA-256)",
        "| Arquivo | Domínio Identificado | Linhas | Tamanho (Bytes) | SHA-256 (Prefixo) | Método de Triagem |",
        "| :--- | :--- | :---: | :---: | :--- | :--- |",
    ])
    for arq in arquivos_inventario:
        md_lines.append(
            f"| `{arq['arquivo']}` | {arq['dominio']} | {arq['linhas_lidas']} | {arq['tamanho_bytes']:,} | `{arq['sha256'][:12]}` | {arq['metodo_triagem']} |"
        )

    md_lines.extend([
        "",
        "---",
        "## 3. Métricas Consolidadas e Hashes das Saídas",
        f"- **Comissões por Lojista:** {len(comissoes_rows)} registros (Total: R$ {total_comissao_brl:.2f})",
        f"- **Notas Fiscais a Emitir:** {len(notas_rows)} registros (Total: R$ {total_notas_brl:.2f})",
        f"- **Divergências de Taxa:** {len(divergencias_rows)} operações contestadas (Total: R$ {total_divergencias_brl:.2f})",
        f"- **Lançamentos Contábeis:** {len(lancamentos_rows)} conciliações bancárias",
        f"- **Pendências Operacionais:** {len(pendencias_rows)} itens para decisão",
        f"- **Rastro Universal:** {len(rastro_rows)} vínculos auditáveis",
        f"- **Hash Combinado de Entradas:** `{hash_entradas_combinado}`",
        f"- **Hash Combinado de Saídas:** `{hash_saidas_combinado}`",
        "",
        "---",
        "## 4. Comparação com Execução Anterior e Governança de Aprovação",
        f"- **Execução Anterior Encontrada:** `{comparacao_execucao['execucao_anterior_encontrada']}`",
        f"- **Entradas Idênticas:** `{comparacao_execucao['entradas_identicas']}`",
        f"- **Saídas Idênticas:** `{comparacao_execucao['saidas_identicas']}`",
        f"- **Herança de Aprovação Bloqueada por Alteração:** `{comparacao_execucao['heranca_aprovacao_bloqueada']}`",
        f"- **Arquivos de Saída Alterados:** `{', '.join(comparacao_execucao['arquivos_saida_alterados']) or 'Nenhum'}`",
        "",
        "---",
        "## 5. Validação da Prova Real do Rastro",
        f"Todos os {prova_real['total_ids_validados']} identificadores de saída (`COM-XXXX`, `NF-XXXX`, `DIV-XXXX`, `LAN-XXXX` e `PEN-XXXX`) foram verificados.",
        "A soma das transações vinculadas no `rastro.csv` é identicamente igual ao valor total reportado em cada relatório oficial.",
        "",
        "---",
        "## 6. Regras e Decisões Aplicadas nesta Execução",
    ])
    for r in manifesto_data["regras_aplicadas_resumo"]:
        md_lines.append(f"- {r}")

    md_content = "\n".join(line.rstrip() for line in md_lines) + "\n"

    for d in output_dirs:
        # JSON atual
        with open(d / "auditoria_execucao.json", "w", encoding="utf-8") as fj:
            json.dump(manifesto_data, fj, indent=2, ensure_ascii=False)
        # Markdown atual
        with open(d / "auditoria_execucao.md", "w", encoding="utf-8") as fmd:
            fmd.write(md_content)
        # Histórico cumulativo de execuções para rastreabilidade entre runs
        hist_path = d / "historico_execucoes.json"
        historico_lista: List[Dict[str, Any]] = []
        if hist_path.exists():
            try:
                with open(hist_path, "r", encoding="utf-8") as fh:
                    loaded_h = json.load(fh)
                    if isinstance(loaded_h, list):
                        historico_lista = loaded_h
            except Exception:
                historico_lista = []
        historico_lista.append({
            "id_execucao": id_execucao,
            "execucao_dir": state["execucao_dir"],
            "data_hora_execucao": now_iso,
            "competencia": competencia,
            "versao_regras": versao_regras,
            "estado_tecnico": estado_tecnico,
            "status_aprovacao": status_aprovacao_final,
            "hash_entradas_combinado": hash_entradas_combinado,
            "hash_saidas_combinado": hash_saidas_combinado,
            "metricas_financeiras": metricas_atuais,
            "comparacao_execucao_anterior": comparacao_execucao,
        })
        with open(hist_path, "w", encoding="utf-8") as fh:
            json.dump(historico_lista, fh, indent=2, ensure_ascii=False)

    return manifesto_data


def emitir_todos_os_entregaveis(
    res_checkout: ResultadoCheckout,
    res_remessas: ResultadoRemessas,
    res_contabil: ResultadoContabil,
    output_dir_local: Path,
    output_dir_oficial: Path,
    state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if state is None:
        raise ValueError("É necessário informar o estado e as fontes para preservar a execução.")
    if not state.get("execucao_stage"):
        state.setdefault("output_dir_oficial", str(output_dir_oficial))
        preparar_execucao(state)

    competencia = state.get("competencia", "2026-09") if state else "2026-09"
    comp_label = format_competencia_br(competencia)

    rastro_completo: List[Dict[str, str]] = []

    # 1. comissoes_por_lojista.csv
    comissoes_rows: List[Dict[str, str]] = []
    idx_com = 1
    map_com_checkout_id: Dict[str, str] = {}
    map_com_remessa_id: Dict[str, str] = {}

    for c in res_checkout.comissoes:
        id_saida = f"COM-{idx_com:04d}"
        idx_com += 1
        map_com_checkout_id[c.cnpj] = id_saida
        comissoes_rows.append({
            "id_saida": id_saida,
            "cnpj": c.cnpj,
            "lojista": c.lojista,
            "linha_negocio": "CHECKOUT",
            "comissao_brl": f"{c.comissao_brl:.2f}",
        })

    for c in res_remessas.comissoes:
        id_saida = f"COM-{idx_com:04d}"
        idx_com += 1
        map_com_remessa_id[c.cnpj] = id_saida
        comissoes_rows.append({
            "id_saida": id_saida,
            "cnpj": c.cnpj,
            "lojista": c.lojista,
            "linha_negocio": "REMESSA",
            "comissao_brl": f"{c.comissao_brl:.2f}",
        })

    # 2. divergencias_taxa.csv
    divergencias_rows: List[Dict[str, str]] = []
    divergencias_objs: List[Tuple[Dict[str, str], Any]] = []
    idx_div = 1
    for d in res_checkout.divergencias:
        id_saida = f"DIV-{idx_div:04d}"
        idx_div += 1
        d_row = {
            "id_saida": id_saida,
            "cnpj": d.cnpj,
            "linha_negocio": "CHECKOUT",
            "ref_origem": d.ref_origem,
            "taxa_contratada_pct": f"{d.taxa_contratada_pct:.2f}",
            "taxa_aplicada_pct": f"{d.taxa_aplicada_pct:.2f}",
            "diferenca_brl": f"{d.diferenca_brl:.2f}",
        }
        divergencias_rows.append(d_row)
        divergencias_objs.append((d_row, d))

    for d in res_remessas.divergencias:
        id_saida = f"DIV-{idx_div:04d}"
        idx_div += 1
        d_row = {
            "id_saida": id_saida,
            "cnpj": d.cnpj,
            "linha_negocio": "REMESSA",
            "ref_origem": d.ref_origem,
            "taxa_contratada_pct": f"{d.taxa_contratada_pct:.2f}",
            "taxa_aplicada_pct": f"{d.taxa_aplicada_pct:.2f}",
            "diferenca_brl": f"{d.diferenca_brl:.2f}",
        }
        divergencias_rows.append(d_row)
        divergencias_objs.append((d_row, d))

    # 3. notas_a_emitir.csv
    notas_rows: List[Dict[str, str]] = []
    idx_nf = 1
    map_nf_checkout_id: Dict[str, str] = {}
    map_nf_remessa_id: str = ""

    for c in res_checkout.comissoes:
        if c.comissao_brl > Decimal("0.00"):
            id_saida = f"NF-{idx_nf:04d}"
            idx_nf += 1
            map_nf_checkout_id[c.cnpj] = id_saida
            notas_rows.append({
                "id_saida": id_saida,
                "tomador_cnpj": c.cnpj,
                "tomador": c.lojista,
                "linha_negocio": "CHECKOUT",
                "valor_brl": f"{c.comissao_brl:.2f}",
                "discriminacao": f"Serviços de intermediação e facilitação de transações comerciais (Checkout) - Competência {comp_label}. Lojista: {c.lojista}.",
            })

    if res_remessas.nota_ponte and res_remessas.nota_ponte.valor_brl > Decimal("0.00"):
        id_saida = f"NF-{idx_nf:04d}"
        idx_nf += 1
        map_nf_remessa_id = id_saida
        notas_rows.append({
            "id_saida": id_saida,
            "tomador_cnpj": res_remessas.nota_ponte.tomador_cnpj,
            "tomador": res_remessas.nota_ponte.tomador,
            "linha_negocio": "REMESSA",
            "valor_brl": f"{res_remessas.nota_ponte.valor_brl:.2f}",
            "discriminacao": res_remessas.nota_ponte.discriminacao,
        })

    # 4. lancamentos_classificados.csv
    lancamentos_rows: List[Dict[str, str]] = []
    origens_lancamentos: Dict[str, str] = {}
    idx_lan = 1
    for l in res_contabil.lancamentos:
        id_saida = f"LAN-{idx_lan:04d}"
        idx_lan += 1
        if not l.arquivo_origem:
            raise ValueError(f"Lançamento {id_saida} sem arquivo de origem bruto.")
        origens_lancamentos[id_saida] = l.arquivo_origem
        lancamentos_rows.append({
            "id_saida": id_saida,
            "banco": l.banco,
            "ref_origem": l.ref_origem,
            "data": l.data,
            "descricao": l.descricao,
            "valor": f"{l.valor:.2f}",
            "conta_codigo": l.conta_codigo,
            "metodo": l.metodo,
            "confianca": f"{l.confianca:.2f}",
        })

    # 5. pendencias.csv
    pendencias_rows: List[Dict[str, str]] = []
    pendencias_objs: List[Tuple[Dict[str, str], Any]] = []
    idx_pen = 1
    for p in res_checkout.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        p_row = {
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        }
        pendencias_rows.append(p_row)
        pendencias_objs.append((p_row, p))

    for p in res_remessas.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        p_row = {
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        }
        pendencias_rows.append(p_row)
        pendencias_objs.append((p_row, p))

    for p in res_contabil.pendencias:
        id_saida = f"PEN-{idx_pen:04d}"
        idx_pen += 1
        p_row = {
            "id_saida": id_saida,
            "tipo": p.tipo,
            "ref_origem": p.ref_origem,
            "valor_brl": f"{p.valor_brl:.2f}",
            "motivo": p.motivo,
            "quem_decide": p.quem_decide,
        }
        pendencias_rows.append(p_row)
        pendencias_objs.append((p_row, p))

    # Índice estruturado para consulta por CNPJ, inclusive sem comissão faturável.
    # Não altera as seis colunas oficiais de pendências nem depende de texto livre.
    state["indice_pendencias_cnpj"] = {}
    for p_row, pendencia in pendencias_objs:
        cnpj = getattr(pendencia, "cnpj", "")
        if cnpj:
            state["indice_pendencias_cnpj"].setdefault(cnpj, []).append(p_row["id_saida"])

    # 6. rastro.csv (Universal Expandido - Organização Barte 14h11)
    # A) Comissões Checkout
    for r in res_checkout.rastro:
        id_com = map_com_checkout_id.get(r.id_saida, r.id_saida)
        rastro_completo.append({
            "id_saida": id_com,
            "arquivo_origem": r.arquivo_origem,
            "ref_origem": r.ref_origem,
            "valor": f"{r.valor:.2f}",
            "regra_aplicada": r.regra_aplicada,
            "taxa_contratada_aplicada": r.taxa_contratada_aplicada,
            "detalhe_calculo": r.detalhe_calculo,
        })

    # B) Comissões Remessa
    for r in res_remessas.rastro:
        id_com = map_com_remessa_id.get(r.id_saida, r.id_saida)
        rastro_completo.append({
            "id_saida": id_com,
            "arquivo_origem": r.arquivo_origem,
            "ref_origem": r.ref_origem,
            "valor": f"{r.valor:.2f}",
            "regra_aplicada": r.regra_aplicada,
            "taxa_contratada_aplicada": r.taxa_contratada_aplicada,
            "detalhe_calculo": r.detalhe_calculo,
        })

    # C) Notas Fiscais Checkout
    for r in res_checkout.rastro:
        id_nf = map_nf_checkout_id.get(r.id_saida)
        if id_nf:
            rastro_completo.append({
                "id_saida": id_nf,
                "arquivo_origem": r.arquivo_origem,
                "ref_origem": r.ref_origem,
                "valor": f"{r.valor:.2f}",
                "regra_aplicada": f"Faturamento NF Checkout ({r.regra_aplicada})",
                "taxa_contratada_aplicada": r.taxa_contratada_aplicada,
                "detalhe_calculo": r.detalhe_calculo,
            })

    # D) Nota Fiscal Ponte Câmbio
    if map_nf_remessa_id:
        for r in res_remessas.rastro:
            rastro_completo.append({
                "id_saida": map_nf_remessa_id,
                "arquivo_origem": r.arquivo_origem,
                "ref_origem": r.ref_origem,
                "valor": f"{r.valor:.2f}",
                "regra_aplicada": "Faturamento NF Ponte Câmbio (Split 50% Spread Remessas)",
                "taxa_contratada_aplicada": r.taxa_contratada_aplicada,
                "detalhe_calculo": r.detalhe_calculo,
            })

    # E) Divergências de Taxa (Checkout e Remessa)
    for d, d_obj in divergencias_objs:
        arq_orig = getattr(d_obj, "arquivo_origem", "") or (
            "01_orbe_relatorio_comissoes_set2026.csv"
            if d["linha_negocio"] == "CHECKOUT"
            else "03_email_ponte_cambio_relatorio_set2026.eml"
        )
        rastro_completo.append({
            "id_saida": d["id_saida"],
            "arquivo_origem": arq_orig,
            "ref_origem": d["ref_origem"],
            "valor": d["diferenca_brl"],
            "regra_aplicada": f"Divergência de Taxa ({d['linha_negocio']}): aplicada {d['taxa_aplicada_pct']}% vs contratada {d['taxa_contratada_pct']}%",
            "taxa_contratada_aplicada": f"{d['taxa_contratada_pct']}%",
            "detalhe_calculo": f"Diferença apurada a favor da Tarvo/Lojista: R$ {d['diferenca_brl']}",
        })

    # F) Lançamentos Bancários Classificados
    for l in lancamentos_rows:
        arq_banco = origens_lancamentos[l["id_saida"]]
        rastro_completo.append({
            "id_saida": l["id_saida"],
            "arquivo_origem": arq_banco,
            "ref_origem": l["ref_origem"],
            "valor": l["valor"],
            "regra_aplicada": f"Classificação contábil ({l['banco']}): conta {l['conta_codigo']} ({l['metodo']})",
            "taxa_contratada_aplicada": "N/A",
            "detalhe_calculo": f"Extrato {l['data']}: {l['descricao']}",
        })

    # G) Pendências Operacionais (com decomposição analítica das contribuições reais quando presentes)
    for p, p_obj in pendencias_objs:
        rastro_itens = getattr(p_obj, "rastro_itens", None) or []
        if rastro_itens:
            for ri in rastro_itens:
                rastro_completo.append({
                    "id_saida": p["id_saida"],
                    "arquivo_origem": ri.arquivo_origem,
                    "ref_origem": ri.ref_origem,
                    "valor": f"{ri.valor:.2f}",
                    "regra_aplicada": ri.regra_aplicada or f"Pendência ({p['tipo']}): {p['motivo']}",
                    "taxa_contratada_aplicada": ri.taxa_contratada_aplicada or "N/A",
                    "detalhe_calculo": ri.detalhe_calculo or f"Decisão requerida por: {p['quem_decide']}",
                })
        else:
            arq_pend = getattr(p_obj, "arquivo_origem", "")
            if not arq_pend:
                arq_pend = "01_orbe_relatorio_comissoes_set2026.csv"
                if p["ref_origem"].startswith("PC-"):
                    arq_pend = "03_email_ponte_cambio_relatorio_set2026.eml"
                elif re.match(r"^L\d+$", p["ref_origem"]) or p["tipo"] in (
                    "CREDITO_NAO_IDENTIFICADO",
                    "TRANSITO_BANCARIO",
                    "REPASSE_DEVOLVIDO",
                    "DEVOLUCAO_SEM_CAUSA",
                    "REPASSE_LOJISTA_BLOQUEADO",
                ):
                    raise ValueError(f"Pendência bancária {p['id_saida']} sem arquivo de origem bruto.")
            rastro_completo.append({
                "id_saida": p["id_saida"],
                "arquivo_origem": arq_pend,
                "ref_origem": p["ref_origem"],
                "valor": p["valor_brl"],
                "regra_aplicada": f"Pendência ({p['tipo']}): {p['motivo']}",
                "taxa_contratada_aplicada": "N/A",
                "detalhe_calculo": f"Decisão requerida por: {p['quem_decide']}",
            })

    # Validação matemática da Prova Real
    prova_real = validar_prova_real(
        comissoes_rows=comissoes_rows,
        notas_rows=notas_rows,
        divergencias_rows=divergencias_rows,
        lancamentos_rows=lancamentos_rows,
        pendencias_rows=pendencias_rows,
        rastro_rows=rastro_completo,
    )

    if not prova_real["valido"]:
        raise ValueError("Prova real inválida; saídas anteriores preservadas: " + "; ".join(prova_real["erros"]))

    # Salva todos os entregáveis canônicos em ambos os destinos ANTES de calcular hashes de saída no manifesto
    outputs_map = {
        "comissoes_por_lojista.csv": (comissoes_rows, ["id_saida", "cnpj", "lojista", "linha_negocio", "comissao_brl"]),
        "divergencias_taxa.csv": (divergencias_rows, ["id_saida", "cnpj", "linha_negocio", "ref_origem", "taxa_contratada_pct", "taxa_aplicada_pct", "diferenca_brl"]),
        "notas_a_emitir.csv": (notas_rows, ["id_saida", "tomador_cnpj", "tomador", "linha_negocio", "valor_brl", "discriminacao"]),
        "lancamentos_classificados.csv": (lancamentos_rows, ["id_saida", "banco", "ref_origem", "data", "descricao", "valor", "conta_codigo", "metodo", "confianca"]),
        "pendencias.csv": (pendencias_rows, ["id_saida", "tipo", "ref_origem", "valor_brl", "motivo", "quem_decide"]),
        "rastro.csv": (rastro_completo, ["id_saida", "arquivo_origem", "ref_origem", "valor", "regra_aplicada", "taxa_contratada_aplicada", "detalhe_calculo"]),
    }

    destinos_unicos = list({output_dir_local.resolve(): output_dir_local, output_dir_oficial.resolve(): output_dir_oficial}.values())
    staged_output = Path(state["execucao_stage"]) / "saida"
    # Histórico de consulta é copiado para o staging; o destino atual permanece intocado.
    for dest in destinos_unicos:
        historico = dest / "historico_execucoes.json"
        if historico.exists():
            import shutil
            shutil.copyfile(historico, staged_output / historico.name)
            break
    for fname, (rows, header) in outputs_map.items():
        for dest_dir in [staged_output]:
            fpath = dest_dir / fname
            with open(fpath, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header, delimiter=";")
                writer.writeheader()
                writer.writerows(rows)

    # Gera os manifestos de auditoria com hashes, cobertura e comparação entre execuções
    manifesto_gerado = gerar_manifestos_auditoria(
        state=state,
        comissoes_rows=comissoes_rows,
        divergencias_rows=divergencias_rows,
        notas_rows=notas_rows,
        lancamentos_rows=lancamentos_rows,
        pendencias_rows=pendencias_rows,
        rastro_rows=rastro_completo,
        prova_real=prova_real,
        output_dirs=[staged_output],
    )
    finalizar_execucao(state, manifesto_gerado, destinos_unicos)

    return {
        "id_execucao": manifesto_gerado["id_execucao"],
        "versao_regras": manifesto_gerado["versao_regras"],
        "estado_tecnico": manifesto_gerado["estado_tecnico"],
        "status_aprovacao": manifesto_gerado["status_aprovacao"],
        "comissoes_count": len(comissoes_rows),
        "divergencias_count": len(divergencias_rows),
        "notas_count": len(notas_rows),
        "lancamentos_count": len(lancamentos_rows),
        "pendencias_count": len(pendencias_rows),
        "rastro_count": len(rastro_completo),
        "prova_real_valida": prova_real["valido"],
        "comparacao_execucao_anterior": manifesto_gerado["comparacao_execucao_anterior"],
    }


