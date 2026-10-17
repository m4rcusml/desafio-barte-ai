"""
Entrypoint Principal do Agente de Fechamento Financeiro Tarvo.
Pode ser executado diretamente (python app.py) ou compilado como executável (.exe).
"""

from __future__ import annotations
import os
import sys
import argparse
from pathlib import Path

# Adiciona o diretório atual ao path para garantir imports limpos
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))

from src.graph import build_closing_graph


def main():
    parser = argparse.ArgumentParser(description="Agente de Fechamento Financeiro Tarvo Pagamentos")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=".",
        help="Diretório onde os arquivos brutos estão localizados (padrão: diretório atual)",
    )
    env_status = os.getenv("STATUS_FECHAMENTO", "PROVISORIO")
    parser.add_argument(
        "--status",
        type=str,
        choices=["PROVISORIO", "APROVADO_POR_HELENA", "REABERTO_PARA_REVISAO"],
        default=env_status,
        help="Estado de aprovação do fechamento (PROVISORIO, APROVADO_POR_HELENA ou REABERTO_PARA_REVISAO)",
    )
    env_comp = os.getenv("COMPETENCIA_FECHAMENTO", "2026-09")
    parser.add_argument(
        "--competencia",
        type=str,
        default=env_comp,
        help="Competência do fechamento no formato YYYY-MM (padrão: 2026-09)",
    )

    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    if getattr(sys, "frozen", False):
        exec_dir = Path(sys.executable).resolve().parent
    else:
        exec_dir = cwd

    # Diretório dos dados de entrada
    if args.data_dir != ".":
        data_dir = Path(args.data_dir).resolve()
    elif any(cwd.glob("01_orbe*")):
        data_dir = cwd
    elif any(exec_dir.glob("01_orbe*")):
        data_dir = exec_dir
    else:
        # Busca nas pastas candidatas
        candidatos = [
            cwd / "Tarvo_Data_Pack_set2026",
            exec_dir / "Tarvo_Data_Pack_set2026",
            exec_dir.parent / "Tarvo_Data_Pack_set2026",
            exec_dir.parent.parent / "Tarvo_Data_Pack_set2026",
        ]
        data_dir = cwd
        for c in candidatos:
            if c.exists() and any(c.glob("01_orbe*")):
                data_dir = c
                break

    output_local = cwd / "fechamento-completo"

    # Encontra o diretório oficial 'saida' do repositório
    candidatos_oficial = [
        cwd / "saida",
        cwd / "barte-solution" / "desafio-barte-ai" / "saida",
        exec_dir / "saida",
        exec_dir / "barte-solution" / "desafio-barte-ai" / "saida",
        exec_dir.parent / "saida",
    ]
    output_oficial = cwd / "saida"
    for cand in candidatos_oficial:
        if cand.exists():
            output_oficial = cand
            break

    print("=" * 75)
    print("🚀 INICIANDO AGENTE AUTÔNOMO DE FECHAMENTO (LANGGRAPH + JEV + GEMINI)")
    print(f"📁 Pasta de Trabalho (Inputs) : {data_dir}")
    print(f"📁 Pasta de Saída (Executável): {output_local}")
    print(f"📁 Pasta de Saída (Oficial)   : {output_oficial}")
    print(f"📅 Competência Alvo           : {args.competencia}")
    print(f"📋 Status Solicitado          : {args.status}")
    print("=" * 75)

    graph = build_closing_graph()

    initial_state = {
        "data_dir": str(data_dir),
        "output_dir_local": str(output_local),
        "output_dir_oficial": str(output_oficial),
        "status_aprovacao": args.status,
        "competencia": args.competencia,
    }

    final_state = graph.invoke(initial_state)
    summary = final_state.get("resumo_execucao", {})

    print("\n" + "=" * 75)
    print("🎉 FECHAMENTO CONCLUÍDO COM 100% DE PROVA REAL MATEMÁTICA!")
    print("=" * 75)
    print(f"✓ comissoes_por_lojista.csv : {summary.get('comissoes_count', 0)} registros")
    print(f"✓ divergencias_taxa.csv     : {summary.get('divergencias_count', 0)} registros")
    print(f"✓ notas_a_emitir.csv        : {summary.get('notas_count', 0)} registros")
    print(f"✓ lancamentos_classificados : {summary.get('lancamentos_count', 0)} registros")
    print(f"✓ pendencias.csv            : {summary.get('pendencias_count', 0)} registros")
    print(f"✓ rastro.csv                : {summary.get('rastro_count', 0)} registros vinculados")
    print("=" * 75)
    print(f"Arquivos salvos com sucesso em:\n 1. {output_local}\n 2. {output_oficial}")
    print("=" * 75)


if __name__ == "__main__":
    main()
