"""
Testes Unitários do Motor de Checkout, 7 Divergências de Bandeira e Estornos Órfãos.
"""

from __future__ import annotations
import sys
import unittest
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.engines.checkout_engine import processar_checkout


class TestCheckoutAndBandeiras(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.workspace_root = cls.repo_root.parent.parent
        cls.data_dir = cls.workspace_root / "Tarvo_Data_Pack_set2026"
        cls.silver_dir = cls.repo_root / "dados_formatados"
        cls.silver_dir.mkdir(parents=True, exist_ok=True)
        cls.f_01 = cls.silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
        cls.f_06 = cls.silver_dir / "06_orbe_ajustes_tardios_formatado.csv"
        cls.f_taxas = cls.silver_dir / "02_tabela_taxas_contratadas_formatado.csv"

    def test_7_divergencias_bandeira_detectadas_e_vinculadas(self):
        """Verifica se os 7 estornos com bandeira divergente geram pendências e mantêm a taxa original."""
        res = processar_checkout([self.f_01, self.f_06], self.f_taxas)
        
        pendencias_bandeira = [
            p for p in res.pendencias if p.tipo == "DIVERGENCIA_CADASTRO_BANDEIRA"
        ]
        self.assertEqual(len(pendencias_bandeira), 7)
        
        refs_esperadas = {
            "TX88447011",
            "TX88447030",
            "TX88447044",
            "TX88447057",
            "TX88447070",
            "TX88447093",
            "TX88447109",
        }
        refs_obtidas = {p.ref_origem for p in pendencias_bandeira}
        self.assertEqual(refs_obtidas, refs_esperadas)
        
        for p in pendencias_bandeira:
            self.assertEqual(p.quem_decide, "Helena")
            self.assertIn("bandeira divergente", p.motivo)

    def test_bloqueio_atlas_idiomas(self):
        """Verifica se a Atlas Idiomas é bloqueada e encaminhada integralmente a pendências."""
        res = processar_checkout([self.f_01, self.f_06], self.f_taxas)
        cnpjs_faturados = {c.cnpj for c in res.comissoes}
        self.assertNotIn("39566044000119", cnpjs_faturados)

        pendencias_atlas = [
            p for p in res.pendencias if p.cnpj == "39566044000119" and p.tipo == "CADASTRO_PENDENTE"
        ]
        self.assertTrue(len(pendencias_atlas) > 0)
        self.assertEqual(pendencias_atlas[0].quem_decide, "Bia / Comercial")

    def test_isencao_casa_do_estudante(self):
        """Verifica se a Casa do Estudante não tem vendas faturadas em setembro e abate estorno de agosto."""
        res = processar_checkout([self.f_01, self.f_06], self.f_taxas)
        
        pendencias_isencao = [
            p for p in res.pendencias if p.tipo == "ISENCAO_NAO_AVISADA" and p.cnpj == "00520815000100"
        ]
        self.assertTrue(len(pendencias_isencao) > 0)

        # O único valor faturado da Casa do Estudante deve ser o estorno da venda prévia de agosto (negativo)
        comissao_casa = next((c for c in res.comissoes if c.cnpj == "00520815000100"), None)
        self.assertIsNotNone(comissao_casa)
        self.assertTrue(comissao_casa.comissao_brl < Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
