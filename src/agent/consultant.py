"""
Subagente Consultivo e de Apresentação da Tarvo Pagamentos.

Atua como assistente consultivo para a equipe financeira (Helena, Caio, Bia)
e diretoria, fornecendo explicações transparentes, rastreabilidade de cálculos
e relatórios de pendências baseados estritamente nos resultados determinísticos.

DIRETRIZ DE SEGURANÇA E GOVERNANÇA:
- NUNCA aprova exceções ou contratos de forma autônoma.
- NUNCA executa pagamentos, liquidações ou operações financeiras externas.
- Todas as decisões permanecem sob responsabilidade humana.
"""

from __future__ import annotations
import argparse
import csv
import json
import sys
import re
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional


from ..utils import format_competencia_br, configurar_saida_utf8


class TarvoConsultant:
    """Subagente consultivo da Tarvo Pagamentos."""

    def __init__(self, output_dir: Optional[Path] = None, competencia: Optional[str] = None):
        if output_dir is None:
            # Tenta encontrar dadas as pastas padrão
            repo_root = Path(__file__).resolve().parent.parent.parent
            cand1 = repo_root / "saida"
            cand2 = repo_root / "fechamento-completo"
            if cand1.exists() and (cand1 / "rastro.csv").exists():
                self.output_dir = cand1
            elif cand2.exists() and (cand2 / "rastro.csv").exists():
                self.output_dir = cand2
            else:
                self.output_dir = cand1
        else:
            self.output_dir = Path(output_dir)
        self.competencia_override = competencia
        if competencia is not None:
            if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", competencia):
                raise ValueError("Competência inválida; use AAAA-MM.")
            efetiva = self._read_manifest().get("competencia")
            if efetiva != competencia:
                raise ValueError(f"Competência solicitada {competencia} difere da saída consultada ({efetiva or 'não identificada'}). Selecione o snapshot correto com --output-dir.")

    def _read_csv(self, filename: str) -> List[Dict[str, str]]:
        path = self.output_dir / filename
        if not path.exists():
            return []
        with open(path, mode="r", encoding="utf-8") as f:
            return list(csv.DictReader(f, delimiter=";"))

    def _read_manifest(self) -> Dict[str, Any]:
        path = self.output_dir / "auditoria_execucao.json"
        if not path.exists():
            return {}
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_summary(self) -> Dict[str, Any]:
        """Gera um resumo executivo dos resultados do fechamento."""
        comissoes = self._read_csv("comissoes_por_lojista.csv")
        notas = self._read_csv("notas_a_emitir.csv")
        divergencias = self._read_csv("divergencias_taxa.csv")
        lancamentos = self._read_csv("lancamentos_classificados.csv")
        pendencias = self._read_csv("pendencias.csv")
        rastro = self._read_csv("rastro.csv")
        manifest = self._read_manifest()

        total_comissao = sum(Decimal(c["comissao_brl"]) for c in comissoes) if comissoes else Decimal("0.00")
        total_notas = sum(Decimal(n["valor_brl"]) for n in notas) if notas else Decimal("0.00")
        total_div = sum(Decimal(d["diferenca_brl"]) for d in divergencias) if divergencias else Decimal("0.00")
        total_pend = sum(Decimal(p["valor_brl"]) for p in pendencias) if pendencias else Decimal("0.00")

        # Agrupamento de pendências por tomador de decisão
        pend_por_decisor: Dict[str, Dict[str, Any]] = {}
        for p in pendencias:
            dec = p["quem_decide"]
            if dec not in pend_por_decisor:
                pend_por_decisor[dec] = {"count": 0, "valor_total": Decimal("0.00"), "tipos": set()}
            pend_por_decisor[dec]["count"] += 1
            pend_por_decisor[dec]["valor_total"] += Decimal(p["valor_brl"])
            pend_por_decisor[dec]["tipos"].add(p["tipo"])

        decisores_serializaveis = {
            k: {
                "count": v["count"],
                "valor_total_brl": f"{v['valor_total']:.2f}",
                "tipos": sorted(list(v["tipos"])),
            }
            for k, v in pend_por_decisor.items()
        }

        comp_raw = manifest.get("competencia", "2026-09")
        comp_fmt = format_competencia_br(comp_raw)
        status_aprov = manifest.get("status_aprovacao", manifest.get("status_fechamento", "PROVISORIO"))
        estado_tec = manifest.get("estado_tecnico", "CONCLUIDO")

        return {
            "competencia": comp_fmt,
            "competencia_iso": comp_raw,
            "id_execucao": manifest.get("id_execucao", ""),
            "versao_regras": manifest.get("versao_regras", ""),
            "estado_tecnico": estado_tec,
            "status_aprovacao": status_aprov,
            "status": f"{status_aprov} (Estado técnico: {estado_tec} - Aguardando Decisões Humanas)",
            "metricas": {
                "total_comissao_brl": f"{total_comissao:.2f}",
                "total_notas_a_emitir_brl": f"{total_notas:.2f}",
                "total_divergencias_taxa_brl": f"{total_div:.2f}",
                "total_exposicao_pendencias_brl": f"{total_pend:.2f}",
                "qtd_comissoes": len(comissoes),
                "qtd_notas": len(notas),
                "qtd_divergencias": len(divergencias),
                "qtd_lancamentos_bancarios": len(lancamentos),
                "qtd_pendencias_humanas": len(pendencias),
                "qtd_vinculos_rastro": len(rastro),
            },
            "pendencias_por_decisor": decisores_serializaveis,
        }

    def explain_lojista(self, query: str) -> Dict[str, Any]:
        """Explica detalhadamente o fechamento de um lojista específico por nome ou CNPJ."""
        def normalizar(value):
            text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().upper()
            return " ".join(re.findall(r"[A-Z0-9]+", text))

        q = normalizar(query)
        if not q:
            return {"erro": "Informe um nome ou CNPJ para a consulta."}
        cnpj_query = re.sub(r"\D", "", query)
        por_cnpj = len(cnpj_query) == 14
        comissoes = self._read_csv("comissoes_por_lojista.csv")
        notas = self._read_csv("notas_a_emitir.csv")
        pendencias = self._read_csv("pendencias.csv")
        rastro = self._read_csv("rastro.csv")

        # Localiza comissões
        tokens = set(q.split())
        if por_cnpj:
            matches_com = [c for c in comissoes if c["cnpj"] == cnpj_query]
        else:
            matches_com = [c for c in comissoes if normalizar(c["lojista"]) == q]
            if not matches_com:
                matches_com = [c for c in comissoes if tokens <= set(normalizar(c["lojista"]).split())]
        if len({c["cnpj"] for c in matches_com}) > 1:
            return {"erro": "Consulta ambígua; informe o CNPJ ou nome completo.",
                    "candidatos": [{"cnpj": c["cnpj"], "lojista": c["lojista"]} for c in matches_com]}

        ids_por_cnpj = self._read_manifest().get("indice_pendencias_cnpj", {})

        if not matches_com:
            # Pode estar bloqueado (ex: Atlas)
            matches_pend = [
                p for p in pendencias
                if (p["id_saida"] in ids_por_cnpj.get(cnpj_query, []) if por_cnpj
                    else tokens <= set(normalizar(p["motivo"]).split()) or q == normalizar(p["ref_origem"]))
            ]
            if matches_pend:
                return {
                    "status": "BLOQUEADO / EM PENDENCIA",
                    "lojista": query,
                    "comissao_brl": "0.00",
                    "motivo": "Lojista com operações bloqueadas ou encaminhadas para validação.",
                    "pendencias": matches_pend,
                }
            return {"erro": f"Nenhum registro encontrado para o lojista/CNPJ '{query}'."}

        com = matches_com[0]
        id_com = com["id_saida"]
        cnpj = com["cnpj"]

        # Vínculos no rastro
        linhas_rastro = [r for r in rastro if r["id_saida"] == id_com]
        nota = next((n for n in notas if n["tomador_cnpj"] == cnpj and n["linha_negocio"] == com["linha_negocio"]), None)
        pends_cli = [p for p in pendencias if p["id_saida"] in ids_por_cnpj.get(cnpj, [])]

        return {
            "id_saida": id_com,
            "cnpj": cnpj,
            "lojista": com["lojista"],
            "linha_negocio": com["linha_negocio"],
            "comissao_brl": com["comissao_brl"],
            "nota_fiscal": nota["id_saida"] if nota else "NÃO EMITIDA (comissão zero ou negativa)",
            "valor_nota_brl": nota["valor_brl"] if nota else "0.00",
            "total_operacoes_vinculadas": len(linhas_rastro),
            "regras_aplicadas": list({r["regra_aplicada"] for r in linhas_rastro}),
            "pendencias_associadas": pends_cli,
            "exemplos_rastro": linhas_rastro[:3],
        }

    def explain_id(self, id_saida: str) -> Dict[str, Any]:
        """Audita e detalha a composição de um ID de saída (COM, NF, DIV, LAN, PEN)."""
        sid = id_saida.strip().upper()
        rastro = self._read_csv("rastro.csv")
        linhas = [r for r in rastro if r["id_saida"] == sid]

        if not linhas:
            return {"erro": f"ID de saída '{id_saida}' não encontrado no rastro.csv."}

        total_somado = sum(Decimal(r["valor"]) for r in linhas)

        return {
            "id_saida": sid,
            "qtd_linhas_vinculadas": len(linhas),
            "soma_matematica_rastro_brl": f"{total_somado:.2f}",
            "arquivo_origem": linhas[0]["arquivo_origem"] if linhas else "",
            "linhas_rastro": linhas,
        }

    def list_pendencias(self, decisor: Optional[str] = None) -> List[Dict[str, str]]:
        """Lista pendências pendentes de decisão humana, opcionalmente filtradas por responsável."""
        pendencias = self._read_csv("pendencias.csv")
        if not decisor:
            return pendencias
        d_upper = decisor.strip().upper()
        return [p for p in pendencias if d_upper in p["quem_decide"].upper()]

    # =========================================================================
    # GUARDRAILS E RESTRIÇÕES DE SEGURANÇA (GOVERNANÇA TARVO)
    # =========================================================================

    def approve_exception(self, pendencia_id: str, homologador: str) -> None:
        """Aprovação autônoma proibida por governança."""
        raise PermissionError(
            f"Ação bloqueada: O subagente não possui autonomia para aprovar a pendência '{pendencia_id}'. "
            f"Exceções comerciais, contábeis e fiscais exigem decisão manual exclusiva de {homologador}."
        )

    def execute_payment(self, destinatario: str, valor_brl: Decimal) -> None:
        """Operações financeiras externas terminantemente proibidas."""
        raise PermissionError(
            f"Ação bloqueada: O subagente não tem autorização para emitir pagamentos, TEDs ou transferências. "
            f"Tentativa de movimentação de R$ {valor_brl:.2f} rejeitada pelo guardrail de segurança."
        )

    def emit_invoice_external(self, nota_id: str) -> None:
        """Emissão fiscal direta no município/SEFAZ proibida."""
        raise PermissionError(
            f"Ação bloqueada: O subagente produz notas propostas em notas_a_emitir.csv para conferência humana. "
            f"A emissão fiscal efetiva deve ser realizada pelo setor fiscal responsável."
        )


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description="Subagente Consultivo Tarvo Pagamentos")
    parser.add_argument("--summary", action="store_true", help="Exibe resumo executivo do fechamento")
    parser.add_argument("--lojista", type=str, help="Consulta e explica fechamento de um lojista por nome ou CNPJ")
    parser.add_argument("--pendencias", type=str, nargs="?", const="ALL", help="Lista pendências por decisor (Helena, Caio, Bia)")
    parser.add_argument("--explain", type=str, help="Audita a composição de um ID (ex: COM-0001, NF-0021, DIV-0001)")
    parser.add_argument("--output-dir", type=str, default=None, help="Diretório das saídas a consultar")
    parser.add_argument("--competencia", type=str, default=None, help="Competência no formato YYYY-MM (opcional)")

    args = parser.parse_args()
    try:
        agent = TarvoConsultant(
            output_dir=Path(args.output_dir) if args.output_dir else None,
            competencia=args.competencia,
        )
    except ValueError as erro:
        parser.error(str(erro))

    if args.summary:
        res = agent.get_summary()
        print("\n" + "=" * 60)
        print("📊 RESUMO EXECUTIVO DO FECHAMENTO (CONSULTA AGÊNTICA)")
        print("=" * 60)
        print(f"Competência               : {res['competencia']}")
        print(f"Status                    : {res['status']}")
        print("-" * 60)
        for k, v in res["metricas"].items():
            print(f"  {k:<30}: {v}")
        print("-" * 60)
        print("PENDÊNCIAS POR DECISOR HUMANO:")
        for dec, info in res["pendencias_por_decisor"].items():
            print(f"  • {dec:<25}: {info['count']:>3} itens | Total R$ {info['valor_total_brl']:>10} | Tipos: {', '.join(info['tipos'])}")
        print("=" * 60 + "\n")

    elif args.lojista:
        res = agent.explain_lojista(args.lojista)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.pendencias:
        dec = None if args.pendencias == "ALL" else args.pendencias
        pends = agent.list_pendencias(dec)
        print(f"\n📋 PENDÊNCIAS EM ABERTO ({len(pends)} encontradas):")
        for p in pends:
            print(f"  [{p['id_saida']}] {p['tipo']:<25} | Ref: {p['ref_origem']:<15} | R$ {p['valor_brl']:>9} | Resp: {p['quem_decide']}")
            print(f"    Motivo: {p['motivo']}\n")

    elif args.explain:
        res = agent.explain_id(args.explain)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    else:
        # Default: mostra o summary
        res = agent.get_summary()
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
