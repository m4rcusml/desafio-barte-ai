"""
Teste de Fechamento Parcial por Dependência (Nível Extra).
Verifica a capacidade de processar subconjuntos de fontes sem travar a execução geral.
"""

from __future__ import annotations
import sys
import unittest
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.graph import node_motores_dominio
from src.state import ClosingState


class TestPartialClosing(unittest.TestCase):

    def test_partial_closing_without_remessas(self):
        """Verifica se o fechamento executa checkout mesmo sem arquivos de remessas ou câmbio."""
        repo_root = Path(__file__).resolve().parent.parent
        silver_dir = repo_root / "dados_formatados"

        state: ClosingState = {
            "data_dir": str(repo_root),
            "output_dir_local": str(repo_root / "fechamento-completo"),
            "output_dir_oficial": str(repo_root / "saida"),
            "silver_paths": {
                "taxas": str(silver_dir / "02_tabela_taxas_contratadas_formatado.csv"),
                "orbe_principal": str(silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"),
            },
            "colisoes_id_detectadas": [],
        }

        res_state = node_motores_dominio(state)
        self.assertIsNotNone(res_state.get("resultado_checkout"))
        self.assertGreater(len(res_state["resultado_checkout"].comissoes), 0)
        # Remessas deve estar vazio sem erro de KeyError
        self.assertEqual(len(res_state["resultado_cambio"].comissoes), 0)

    def test_full_closing_without_arquivo_06(self):
        """Verifica se o sistema executa o grafo completo com sucesso absoluto mesmo na ausência do arquivo 06."""
        import tempfile
        import shutil
        from src.graph import build_closing_graph

        with tempfile.TemporaryDirectory() as tmp_in, tempfile.TemporaryDirectory() as tmp_out:
            data_dir = repo_root.parent.parent / "Tarvo_Data_Pack_set2026"
            # Copia todos os arquivos do data pack exceto o 06
            for f in data_dir.glob("*"):
                if "06" not in f.name:
                    shutil.copy(f, Path(tmp_in) / f.name)

            app = build_closing_graph()
            state: ClosingState = {
                "data_dir": str(tmp_in),
                "output_dir_local": str(tmp_out),
                "output_dir_oficial": str(tmp_out),
            }
            final_state = app.invoke(state)

            self.assertIsNotNone(final_state.get("resultado_checkout"))
            self.assertGreater(len(final_state["resultado_checkout"].comissoes), 0)

            # Garante que todos os 6 CSVs foram gerados normalmente
            gerados = {p.name for p in Path(tmp_out).glob("*.csv")}
            esperados = {
                "comissoes_por_lojista.csv",
                "divergencias_taxa.csv",
                "notas_a_emitir.csv",
                "lancamentos_classificados.csv",
                "pendencias.csv",
                "rastro.csv",
            }
            self.assertTrue(esperados.issubset(gerados))


if __name__ == "__main__":
    unittest.main()
