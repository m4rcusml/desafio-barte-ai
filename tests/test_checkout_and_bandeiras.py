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
from src.engines.cambio_engine import processar_remessas
from src.formatters.orbe_formatter import format_orbe_file
from src.formatters.taxas_formatter import format_taxas_file


class TestCheckoutAndBandeiras(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import shutil
        import tempfile
        import zipfile
        cls._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(cls._tmpdir.name)
        cls.repo_root = Path(__file__).resolve().parent.parent
        zip_path = cls.repo_root / "dados" / "originais" / "Tarvo_Data_Pack_set2026.zip"
        f06_orig = cls.repo_root / "dados" / "originais" / "06_orbe_ajustes_tardios_set2026.csv"

        cls.data_dir = tmp_path / "raw"
        cls.data_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(cls.data_dir)
        shutil.copy(f06_orig, cls.data_dir / f06_orig.name)

        cls.silver_dir = tmp_path / "silver"
        cls.silver_dir.mkdir(parents=True, exist_ok=True)
        cls.f_01 = cls.silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
        cls.f_06 = cls.silver_dir / "06_orbe_ajustes_tardios_formatado.csv"
        cls.f_taxas = cls.silver_dir / "02_tabela_taxas_contratadas_formatado.csv"

        format_orbe_file(cls.data_dir / "01_orbe_relatorio_comissoes_set2026.csv", cls.f_01)
        format_orbe_file(cls.data_dir / "06_orbe_ajustes_tardios_set2026.csv", cls.f_06)
        format_taxas_file(cls.data_dir / "02_tabela_taxas_contratadas.xlsx", cls.f_taxas)

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def test_7_divergencias_bandeira_detectadas_e_vinculadas(self):
        """Verifica se os 7 estornos com bandeira divergente mantêm a taxa original e preservam evidência no rastro."""
        res = processar_checkout([self.f_01, self.f_06], self.f_taxas)

        pendencias_bandeira = [
            p for p in res.pendencias if p.tipo == "DIVERGENCIA_CADASTRO_BANDEIRA"
        ]
        # Conforme homologado por Helena: bandeiras divergentes não geram pendência nem contestação
        self.assertEqual(len(pendencias_bandeira), 0)

        refs_esperadas = {
            "TX88447011",
            "TX88447030",
            "TX88447044",
            "TX88447057",
            "TX88447070",
            "TX88447093",
            "TX88447109",
        }

        rastro_map = {r.ref_origem: r for r in res.rastro}
        for ref_id in refs_esperadas:
            self.assertIn(ref_id, rastro_map)
            detalhe = rastro_map[ref_id].detalhe_calculo
            self.assertIn("vínculo por referência homologado por Helena", detalhe)

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

    def test_isencao_casa_do_estudante_e_118_itens_no_rastro(self):
        """Verifica se a Casa do Estudante preserva a pendência consolidada com as 118 transações Orbe no rastro."""
        res = processar_checkout([self.f_01, self.f_06], self.f_taxas)

        pendencias_isencao = [
            p for p in res.pendencias if p.tipo == "ISENCAO_NAO_AVISADA" and p.cnpj == "00520815000100"
        ]
        self.assertEqual(len(pendencias_isencao), 1)
        pen_casa = pendencias_isencao[0]
        self.assertEqual(pen_casa.valor_brl, Decimal("15396.77"))
        self.assertEqual(len(pen_casa.rastro_itens), 118)
        self.assertEqual(sum(r.valor for r in pen_casa.rastro_itens), Decimal("15396.77"))
        for r_item in pen_casa.rastro_itens:
            self.assertEqual(r_item.arquivo_origem, "01_orbe_relatorio_comissoes_set2026.csv")
            self.assertTrue(r_item.ref_origem.startswith(("TX", "AN")))

        # O único valor faturado da Casa do Estudante deve ser o estorno da venda prévia de agosto (-5.50)
        comissao_casa = next((c for c in res.comissoes if c.cnpj == "00520815000100"), None)
        self.assertIsNotNone(comissao_casa)
        self.assertEqual(comissao_casa.comissao_brl, Decimal("-5.50"))

    def test_deduplicacao_exata_vs_bloqueio_conflito_orbe(self):
        """Verifica que duplicatas idênticas na Orbe são deduplicadas com evidência e IDs conflitantes bloqueiam AMBAS as versões."""
        import csv
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            f_lote1 = Path(tmpdir) / "01_orbe_lote1.csv"
            f_lote2 = Path(tmpdir) / "06_orbe_tardio.csv"
            header = [
                "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                "tipo_lancamento", "modalidade", "qtd_parcelas", "bandeira", "valor_bruto",
                "taxa_aplicada_pct", "valor_taxa", "valor_liquido", "id_referencia", "data_venda_original",
            ]
            with open(f_lote1, "w", encoding="utf-8", newline="") as f1:
                w1 = csv.writer(f1, delimiter=";")
                w1.writerow(header)
                # TX_ID_EXATA: aparecerá idêntica no lote 2
                w1.writerow(["TX_ID_EXATA", "2026-09-10", "1014537966", "Dublin Hub", "1", "1", "1", "3", "1000.00", "2.59", "25.90", "974.10", "", ""])
                # TX_ID_CONFLITO: aparecerá com valor_bruto diferente no lote 2 -> AMBAS devem ser bloqueadas!
                w1.writerow(["TX_ID_CONFLITO", "2026-09-12", "1014537966", "Dublin Hub", "1", "1", "1", "3", "2000.00", "2.59", "51.80", "1948.20", "", ""])

            with open(f_lote2, "w", encoding="utf-8", newline="") as f2:
                w2 = csv.writer(f2, delimiter=";")
                w2.writerow(header)
                w2.writerow(["TX_ID_EXATA", "2026-09-10", "1014537966", "Dublin Hub", "1", "1", "1", "3", "1000.00", "2.59", "25.90", "974.10", "", ""])
                w2.writerow(["TX_ID_CONFLITO", "2026-09-12", "1014537966", "Dublin Hub", "1", "1", "1", "3", "3500.00", "2.59", "90.65", "3409.35", "", ""])

            res = processar_checkout([f_lote1, f_lote2], self.f_taxas, competencia="2026-09")

            # Apenas TX_ID_EXATA deve entrar em comissões (1000 * 2.59% = 25.90); TX_ID_CONFLITO teve AMBAS as versões bloqueadas
            self.assertEqual(len(res.comissoes), 1)
            self.assertEqual(res.comissoes[0].comissao_brl, Decimal("25.90"))
            self.assertEqual(res.comissoes[0].transacoes_count, 1)
            self.assertIn("Deduplicado: 2 ocorrências idênticas", res.rastro[0].detalhe_calculo)

            # Pendência de conflito gerada com as 2 versões bloqueadas no rastro_itens
            pends_conf = [p for p in res.pendencias if p.tipo == "DUPLICIDADE_CONFLITANTE"]
            self.assertEqual(len(pends_conf), 1)
            self.assertEqual(pends_conf[0].ref_origem, "TX_ID_CONFLITO")
            self.assertEqual(len(pends_conf[0].rastro_itens), 2)
            self.assertEqual(pends_conf[0].valor_brl, Decimal("51.80") + Decimal("90.65"))

    def test_deduplicacao_exata_vs_bloqueio_conflito_ponte(self):
        """Verifica que na Ponte Câmbio cópias exatas entram 1 vez e IDs conflitantes têm AMBAS as ocorrências bloqueadas."""
        import csv
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            f_ponte_test = Path(tmpdir) / "ponte_conflito.csv"
            header = [
                "num_operacao", "data_contratacao", "data_liquidacao", "cnpj_cliente",
                "cliente", "moeda", "valor_me", "taxa_cliente", "ptax_ref",
                "valor_brl", "spread_brl", "spread_pct", "spread_estimado_brl",
                "iof_brl", "status_compliance", "observacao",
            ]
            with open(f_ponte_test, "w", encoding="utf-8", newline="") as fp:
                w = csv.writer(fp, delimiter=";")
                w.writerow(header)
                # Cópia exata (difere apenas em observacao): processa 1x (50% de 800 = 400.00)
                w.writerow(["PC-0926-9001", "2026-09-10", "2026-09-11", "15802576000140", "Dublin Hub", "USD", "10000.00", "5.0800", "5.0000", "50800.00", "800.00", "0.0160", "800.00", "193.04", "APROVADO", ""])
                w.writerow(["PC-0926-9001", "2026-09-10", "2026-09-11", "15802576000140", "Dublin Hub", "USD", "10000.00", "5.0800", "5.0000", "50800.00", "800.00", "0.0160", "800.00", "193.04", "APROVADO", "reprocessada"])
                # Conflito de valores para o mesmo num_operacao: AMBAS bloqueadas!
                w.writerow(["PC-0926-9002", "2026-09-15", "2026-09-16", "15802576000140", "Dublin Hub", "USD", "10000.00", "5.0800", "5.0000", "50800.00", "800.00", "0.0160", "800.00", "193.04", "APROVADO", "v1"])
                w.writerow(["PC-0926-9002", "2026-09-15", "2026-09-16", "15802576000140", "Dublin Hub", "USD", "12000.00", "5.0800", "5.0000", "60960.00", "960.00", "0.0160", "960.00", "231.65", "APROVADO", "v2"])

            res = processar_remessas(f_ponte_test, self.f_taxas, competencia="2026-09")

            # Apenas PC-0926-9001 entra (50% de 800.00 = 400.00); PC-0926-9002 foi integralmente bloqueada
            self.assertEqual(res.total_comissao_tarvo, Decimal("400.00"))
            self.assertEqual(res.nota_ponte.valor_brl, Decimal("400.00"))
            self.assertEqual(len(res.comissoes), 1)
            self.assertEqual(res.comissoes[0].operacoes_count, 1)

            pen_conflito = next(p for p in res.pendencias if p.ref_origem == "PC-0926-9002")
            self.assertIn("valores conflitantes", pen_conflito.motivo)
            self.assertEqual(pen_conflito.valor_brl, Decimal("800.00") + Decimal("960.00"))
            self.assertEqual(len(pen_conflito.rastro_itens), 2)


if __name__ == "__main__":
    unittest.main()

