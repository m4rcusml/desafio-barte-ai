"""
Testes Unitários da Camada de Conciliação Bancária, Extrato Aurora e CNPJ Ponte.
"""

from __future__ import annotations
import sys
import unittest
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.engines.banking_engine import classificar_extratos
from src.formatters.aurora_formatter import format_aurora_file
from src.engines.cambio_engine import processar_remessas


class TestBankingAndAurora(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.workspace_root = cls.repo_root.parent.parent
        cls.data_dir = cls.workspace_root / "Tarvo_Data_Pack_set2026"
        cls.silver_dir = cls.data_dir / "dados_formatados"
        cls.raw_aurora = cls.data_dir / "05a_extrato_banco_aurora_cc4471_set2026.csv"
        cls.f_ponte = cls.silver_dir / "03_ponte_cambio_operacoes_formatado.csv"
        cls.f_taxas = cls.silver_dir / "02_tabela_taxas_contratadas_formatado.csv"

    def test_aurora_formatter_physical_lines_and_descriptions(self):
        """Verifica se o formatador do Aurora preserva a linha física e descrição preenchida."""
        out_p, count = format_aurora_file(self.raw_aurora, self.silver_dir)
        self.assertEqual(count, 84)

        with open(out_p, "r", encoding="utf-8") as f:
            lines = [l.strip().split(";") for l in f if l.strip()]

        headers = lines[0]
        self.assertIn("linha_fisica", headers)
        self.assertIn("lancamento", headers)

        # Primeira transação física é na linha L9 e última L92
        first_row = lines[1]
        last_row = lines[-1]
        col_lf = headers.index("linha_fisica")
        col_desc = headers.index("lancamento")

        self.assertEqual(first_row[col_lf], "9")
        self.assertEqual(last_row[col_lf], "92")
        self.assertTrue(len(first_row[col_desc]) > 0)
        self.assertTrue(len(last_row[col_desc]) > 0)

    def test_banking_engine_rules_and_pendencias(self):
        """Verifica classificação de regras bancárias, ausência de fake IA e pendências ativadas."""
        res = classificar_extratos(self.silver_dir)
        self.assertTrue(len(res.lancamentos) > 0)

        # Nenhuma linha deve ter metodo == 'IA' sem chamada real
        metodos = {l.metodo for l in res.lancamentos}
        self.assertNotIn("IA", metodos)

        # Verifica pendência de PIX sem identificação (L50)
        pen_pix = next((p for p in res.pendencias if p.tipo == "CREDITO_NAO_IDENTIFICADO"), None)
        self.assertIsNotNone(pen_pix)
        self.assertEqual(pen_pix.ref_origem, "L50")
        self.assertEqual(pen_pix.valor_brl, Decimal("7350.00"))
        self.assertEqual(pen_pix.quem_decide, "Helena / Financeiro")

        # Verifica pendência de devolução sem causa (L65)
        pen_dev = next((p for p in res.pendencias if p.tipo == "DEVOLUCAO_SEM_CAUSA"), None)
        self.assertIsNotNone(pen_dev)
        self.assertEqual(pen_dev.ref_origem, "L65")
        self.assertEqual(pen_dev.valor_brl, Decimal("12400.00"))
        self.assertEqual(pen_dev.quem_decide, "Helena / Comercial")

        # Verifica trânsito bancário 300k em 30/09 (L92)
        pen_transito = next((p for p in res.pendencias if p.tipo == "TRANSITO_BANCARIO"), None)
        self.assertIsNotNone(pen_transito)
        self.assertEqual(pen_transito.ref_origem, "L92")
        self.assertEqual(pen_transito.valor_brl, Decimal("300000.00"))
        self.assertEqual(pen_transito.quem_decide, "Caio / Conciliação Bancária")

    def test_ponte_cambio_cnpj_and_negatives(self):
        """Verifica se o tomador da Ponte possui o CNPJ 75374179000146 e negativos excluídos."""
        res = processar_remessas(self.f_ponte, self.f_taxas)
        self.assertEqual(res.nota_ponte.tomador_cnpj, "75374179000146")

        # Verifica pendências de spread negativo
        pens_neg = [p for p in res.pendencias if p.tipo == "SPREAD_NEGATIVO_CONTESTACAO"]
        self.assertEqual(len(pens_neg), 4)
        for p in pens_neg:
            self.assertEqual(p.quem_decide, "Helena")


if __name__ == "__main__":
    unittest.main()
