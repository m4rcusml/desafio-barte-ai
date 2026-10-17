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
from src.formatters.taxas_formatter import format_taxas_file
from src.graph import build_closing_graph
from src.agent.consultant import TarvoConsultant


class TestOutubroSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import zipfile
        cls._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(cls._tmpdir.name)
        cls.repo_root = Path(__file__).resolve().parent.parent
        zip_path = cls.repo_root / "dados" / "originais" / "Tarvo_Data_Pack_set2026.zip"

        cls.raw_dir = tmp_path / "raw"
        cls.raw_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(cls.raw_dir)

        cls.taxas_path = tmp_path / "02_tabela_taxas_contratadas_formatado.csv"
        format_taxas_file(cls.raw_dir / "02_tabela_taxas_contratadas.xlsx", cls.taxas_path)

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

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
                writer.writerow([
                    "TX_OUT_0001", "2026-10-15", "1018325654", "Casa do Estudante",
                    "1", "1", "1", "1000.00", "2.69", "26.90", "973.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path, competencia="2026-10")

            comissao_casa = next((c for c in res.comissoes if c.cnpj == "00520815000100"), None)
            self.assertIsNone(comissao_casa)

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
                writer.writerow([
                    "TX_2027_0001", "2027-01-10", "1018325654", "Casa do Estudante",
                    "1", "1", "1", "1000.00", "2.69", "26.90", "973.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path, competencia="2027-01")

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
                writer.writerow([
                    "TX_OUT_0002", "2026-10-05", "1075624862", "Escola Bridge",
                    "1", "4", "1", "1000.00", "1.39", "13.90", "986.10", "1", "", ""
                ])

            res = processar_checkout([tmp_csv], self.taxas_path, competencia="2026-10")
            com_bridge = next((c for c in res.comissoes if c.cnpj == "22224579000109"), None)
            self.assertIsNotNone(com_bridge)
            linha_rastro = res.rastro[0]
            self.assertIn("pós-15/09", linha_rastro.regra_aplicada)

    def test_fluxo_completo_outubro_end_to_end_sem_contaminar_setembro(self):
        """Executa o grafo completo para 2026-10 validando notas, manifesto, consultor e busca histórica de setembro."""
        import shutil
        with tempfile.TemporaryDirectory() as tmp_root:
            root_p = Path(tmp_root)
            in_dir = root_p / "inputs_outubro"
            out_local = root_p / "fechamento-completo"
            out_oficial = root_p / "saida"
            in_dir.mkdir(parents=True, exist_ok=True)

            # Copia base histórica de setembro (01) e tabela de contratos (02) + plano de contas (04)
            shutil.copy(
                self.raw_dir / "01_orbe_relatorio_comissoes_set2026.csv",
                in_dir / "01_orbe_relatorio_comissoes_set2026.csv",
            )
            shutil.copy(
                self.raw_dir / "02_tabela_taxas_contratadas.xlsx",
                in_dir / "02_tabela_taxas_contratadas.xlsx",
            )
            shutil.copy(
                self.raw_dir / "04_plano_de_contas_fenix_erp.csv",
                in_dir / "04_plano_de_contas_fenix_erp.csv",
            )

            # Cria arquivo Orbe de movimentos de outubro (06_orbe_ajustes_tardios_out2026.csv)
            f_out_orbe = in_dir / "06_orbe_ajustes_tardios_out2026.csv"
            with open(f_out_orbe, mode="w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow([
                    "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                    "tipo_lancamento", "modalidade", "qtd_parcelas", "bandeira", "valor_bruto",
                    "taxa_aplicada_pct", "valor_taxa", "valor_liquido", "id_referencia", "data_venda_original",
                ])
                # 1) Venda Bridge Idiomas em 05/10/2026 (Crédito à vista -> vigência pós-15/09 = 2.19% -> R$ 21.90)
                w.writerow([
                    "TX_OUT_BRIDGE_VENDA", "05/10/2026", "1075624862", "BRIDGE IDIOMAS",
                    "VENDA", "CREDITO A VISTA", "1", "VISA", "1000,00", "2,19", "21,90", "978,10", "", "",
                ])
                # 2) Estorno em 18/10/2026 referenciando venda TX88411267 (de 01/09/2026 em 01, pré-15/09 = 2.59% -> R$ -25.90)
                # Sem data_venda_original preenchida para testar busca histórica via tx_primarias!
                w.writerow([
                    "TX_OUT_BRIDGE_EST_HIST", "18/10/2026", "1075624862", "BRIDGE IDIOMAS",
                    "ESTORNO", "CREDITO A VISTA", "1", "VISA", "-1000,00", "2,19", "-21,90", "-978,10", "TX88411267", "",
                ])
                # 3) Venda Dublin Hub em 12/10/2026 (Crédito à vista -> 2.59% -> R$ 51.80)
                w.writerow([
                    "TX_OUT_DUBLIN_VENDA", "12/10/2026", "1014537966", "DUBLIN HUB INTERCAMBIO",
                    "VENDA", "CREDITO A VISTA", "1", "VISA", "2000,00", "2,59", "51,80", "1948,20", "", "",
                ])
                # 4) Venda Casa do Estudante em 20/10/2026 (Isenta em set-dez -> pendência R$ 26.90)
                w.writerow([
                    "TX_OUT_CASA_ISENTA", "20/10/2026", "1018325654", "CASA DO ESTUDANTE",
                    "VENDA", "CREDITO A VISTA", "1", "MASTERCARD", "1000,00", "2,69", "26,90", "973,10", "", "",
                ])

            graph = build_closing_graph()
            final_state = graph.invoke({
                "data_dir": str(in_dir),
                "output_dir_local": str(out_local),
                "output_dir_oficial": str(out_oficial),
                "status_aprovacao": "PROVISORIO",
                "competencia": "2026-10",
            })

            self.assertTrue(final_state["prova_real_valida"])

            # Verifica que NENHUMA transação de setembro entrou nas comissões de outubro
            res_chk = final_state["resultado_checkout"]
            com_map = {c.cnpj: c for c in res_chk.comissoes}
            self.assertEqual(set(com_map.keys()), {"22224579000109", "68567965000102"})
            # Bridge: +21.90 (venda out a 2.19%) - 25.90 (estorno venda 01/09 a 2.59%) = -4.00
            self.assertEqual(com_map["22224579000109"].comissao_brl, Decimal("-4.00"))
            # Dublin: +51.80
            self.assertEqual(com_map["68567965000102"].comissao_brl, Decimal("51.80"))

            # Verifica discriminação de Competência 10/2026 nas notas a emitir
            with open(out_oficial / "notas_a_emitir.csv", "r", encoding="utf-8") as fnf:
                notas_out = list(csv.DictReader(fnf, delimiter=";"))
            self.assertEqual(len(notas_out), 1)
            self.assertIn("Competência 10/2026", notas_out[0]["discriminacao"])

            # Verifica consultor agêntico lendo a competência 10/2026 do manifesto
            consultant = TarvoConsultant(output_dir=out_oficial)
            summary = consultant.get_summary()
            self.assertEqual(summary["competencia"], "10/2026")
            self.assertEqual(summary["competencia_iso"], "2026-10")


if __name__ == "__main__":
    unittest.main()

