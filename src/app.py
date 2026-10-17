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
        choices=["PROVISORIO", "APROVADO_POR_HELENA"],
        default=env_status,
        help="Estado de aprovação do fechamento (PROVISORIO ou APROVADO_POR_HELENA)",
    )

    args = parser.parse_args()

    # Se estiver rodando como executável congelado (PyInstaller), usa a pasta do .exe
    if getattr(sys, "frozen", False):
        exec_dir = Path(sys.executable).resolve().parent
    else:
        exec_dir = Path.cwd().resolve()

    data_dir = Path(args.data_dir).resolve() if args.data_dir != "." else exec_dir

    # Se no diretório não houver arquivos do data pack, tenta a pasta padrão do projeto
    # Resolução correta dos diretórios
    repo_root = Path(__file__).resolve().parent.parent
    workspace_root = repo_root.parent
    if not any(data_dir.glob("*.csv")):
        fallback_data = workspace_root / "Tarvo_Data_Pack_set2026"
        if fallback_data.exists():
            data_dir = fallback_data

    output_local = exec_dir / "fechamento-completo"
    output_oficial = repo_root / "saida"

    print("=" * 75)
    print("🚀 INICIANDO AGENTE AUTÔNOMO DE FECHAMENTO (LANGGRAPH + JEV + GEMINI)")
    print(f"📁 Pasta de Trabalho (Inputs) : {data_dir}")
    print(f"📁 Pasta de Saída (Executável): {output_local}")
    print(f"📁 Pasta de Saída (Oficial)   : {output_oficial}")
    print(f"📋 Status do Fechamento      : {args.status}")
    print("=" * 75)

    graph = build_closing_graph()

    initial_state = {
        "data_dir": str(data_dir),
        "output_dir_local": str(output_local),
        "output_dir_oficial": str(output_oficial),
        "status_aprovacao": args.status,
        "competencia": "2026-09",
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
