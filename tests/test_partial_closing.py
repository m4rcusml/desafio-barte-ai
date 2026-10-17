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


if __name__ == "__main__":
    unittest.main()
