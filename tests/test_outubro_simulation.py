"""
Teste de Simulação e Generalização para Outubro/2026 (Nível Extra).
Demonstra a parametrização de competência, vigências e o limite temporal da isenção da Casa do Estudante (set-dez/2026),
sem alteração no algoritmo e sem contaminação dos dados de setembro.
"""

from __future__ import annotations
import csv
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.engines.checkout_engine import processar_checkout


class TestOutubroSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.taxas_path = cls.repo_root / "dados_formatados" / "02_tabela_taxas_contratadas_formatado.csv"

    def test_outubro_isencao_casa_do_estudante_permanece_ativa(self):
        """Verifica se em outubro/2026 a Casa do Estudante continua isenta (período set-dez/2026)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_csv = Path(tmpdir) / "orbe_outubro_mock.csv"
            with open(tmp_csv, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                    "tipo_lancamento", "modalidade", "qtd_parcelas", "valor_bruto", "taxa_aplicada_pct",
                    "valor_taxa", "valor_liquido", "bandeira", "id_referencia", "data_venda_original"
                ])
                # Transação em 15/10/2026 com taxa indevidamente aplicada pela adquirente
                writer.writerow([
                    "TX_OUT_0001", "2026-10-15", "1018325654", "Casa do Estudante",
                    "1", "1", "1", "1000.00", "2.69", "26.90", "973.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path)

            # Não deve faturar comissão comercial de venda (permanece isenta)
            comissao_casa = next((c for c in res.comissoes if c.cnpj == "00520815000100"), None)
            self.assertIsNone(comissao_casa)

            # Gera pendência de isenção não avisada para a devolução
            pends_casa = [p for p in res.pendencias if p.cnpj == "00520815000100" and p.tipo == "ISENCAO_NAO_AVISADA"]
            self.assertEqual(len(pends_casa), 1)
            self.assertEqual(pends_casa[0].valor_brl, Decimal("26.90"))

    def test_janeiro_2027_isencao_casa_expira(self):
        """Verifica se após 31/12/2026 a isenção da Casa do Estudante cessa e taxa contratual passa a ser cobrada."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_csv = Path(tmpdir) / "orbe_2027_mock.csv"
            with open(tmp_csv, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                    "tipo_lancamento", "modalidade", "qtd_parcelas", "valor_bruto", "taxa_aplicada_pct",
                    "valor_taxa", "valor_liquido", "bandeira", "id_referencia", "data_venda_original"
                ])
                # Transação em 10/01/2027 após o término da isenção comercial
                writer.writerow([
                    "TX_2027_0001", "2027-01-10", "1018325654", "Casa do Estudante",
                    "1", "1", "1", "1000.00", "2.69", "26.90", "973.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path)

            # Agora deve faturar normalmente pela tabela contratual
            comissao_casa = next((c for c in res.comissoes if c.cnpj == "00520815000100"), None)
            self.assertIsNotNone(comissao_casa)
            self.assertGreater(comissao_casa.comissao_brl, Decimal("0.00"))

    def test_outubro_bridge_idiomas_aplica_taxa_pos_15_setembro(self):
        """Verifica se em outubro a Bridge Idiomas aplica integralmente a vigência contratual mais recente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_csv = Path(tmpdir) / "orbe_bridge_outubro.csv"
            with open(tmp_csv, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                    "tipo_lancamento", "modalidade", "qtd_parcelas", "valor_bruto", "taxa_aplicada_pct",
                    "valor_taxa", "valor_liquido", "bandeira", "id_referencia", "data_venda_original"
                ])
                # Venda Débito em 05/10/2026: taxa pós-15/09 deve ser aplicada
                writer.writerow([
                    "TX_OUT_0002", "2026-10-05", "1075624862", "Escola Bridge",
                    "1", "0", "1", "1000.00", "1.39", "13.90", "986.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path)
            com_bridge = next((c for c in res.comissoes if c.cnpj == "22224579000109"), None)
            self.assertIsNotNone(com_bridge)
            # Verifica rastro
            linha_rastro = res.rastro[0]
            self.assertIn("pós-15/09", linha_rastro.regra_aplicada)


if __name__ == "__main__":
    unittest.main()
