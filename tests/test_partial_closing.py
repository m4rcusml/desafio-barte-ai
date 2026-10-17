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

from src.graph import node_motores_dominio, build_closing_graph
from src.state import ClosingState
from src.formatters.orbe_formatter import format_orbe_file
from src.formatters.taxas_formatter import format_taxas_file


class TestPartialClosing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import tempfile
        import zipfile
        cls._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(cls._tmpdir.name)
        cls.repo_root = Path(__file__).resolve().parent.parent
        zip_path = cls.repo_root / "dados" / "originais" / "Tarvo_Data_Pack_set2026.zip"

        cls.raw_dir = tmp_path / "raw"
        cls.raw_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(cls.raw_dir)

        cls.silver_dir = tmp_path / "silver"
        cls.silver_dir.mkdir(parents=True, exist_ok=True)
        cls.f_orbe = cls.silver_dir / "01_orbe_relatorio_comissoes_formatado.csv"
        cls.f_taxas = cls.silver_dir / "02_tabela_taxas_contratadas_formatado.csv"
        format_orbe_file(cls.raw_dir / "01_orbe_relatorio_comissoes_set2026.csv", cls.f_orbe)
        format_taxas_file(cls.raw_dir / "02_tabela_taxas_contratadas.xlsx", cls.f_taxas)

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def test_partial_closing_without_remessas(self):
        """Verifica se o fechamento executa checkout mesmo sem arquivos de remessas ou câmbio."""
        state: ClosingState = {
            "data_dir": str(self.raw_dir),
            "output_dir_local": str(self.silver_dir / "out_local"),
            "output_dir_oficial": str(self.silver_dir / "out_oficial"),
            "silver_paths": {
                "taxas": str(self.f_taxas),
                "orbe_principal": str(self.f_orbe),
            },
            "colisoes_id_detectadas": [],
        }

        res_state = node_motores_dominio(state)
        self.assertIsNotNone(res_state.get("resultado_checkout"))
        self.assertGreater(len(res_state["resultado_checkout"].comissoes), 0)
        self.assertEqual(len(res_state["resultado_cambio"].comissoes), 0)

    def test_full_closing_without_arquivo_06(self):
        """Sem o complemento obrigatório 06, setembro continua parcial e gera pendência."""
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as tmp_root:
            root_p = Path(tmp_root)
            tmp_in = root_p / "in"
            tmp_out = root_p / "out"
            tmp_in.mkdir(parents=True, exist_ok=True)
            tmp_out.mkdir(parents=True, exist_ok=True)

            for f in self.raw_dir.glob("*"):
                if "06" not in f.name:
                    shutil.copy(f, tmp_in / f.name)

            app = build_closing_graph()
            state: ClosingState = {
                "data_dir": str(tmp_in),
                "output_dir_local": str(tmp_out),
                "output_dir_oficial": str(tmp_out),
            }
            final_state = app.invoke(state)

            self.assertIsNotNone(final_state.get("resultado_checkout"))
            self.assertGreater(len(final_state["resultado_checkout"].comissoes), 0)
            self.assertEqual(final_state["cobertura_fontes"]["ORBE_AJUSTES_TARDIOS"]["estado"], "AUSENTE")
            self.assertTrue(final_state["cobertura_fontes"]["ORBE_AJUSTES_TARDIOS"]["obrigatorio"])
            self.assertEqual(final_state["estado_tecnico"], "PARCIAL_COM_BLOQUEIOS")
            faltantes = [p for p in final_state["resultado_checkout"].pendencias
                         if p.tipo == "FONTE_OBRIGATORIA_AUSENTE"]
            self.assertTrue(any(p.ref_origem == "ORBE_AJUSTES_TARDIOS" for p in faltantes))

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

    def test_distincao_ausente_invalida_valida_sem_movimentos_e_dependencia(self):
        """Verifica distinção entre fonte AUSENTE, INVALIDA, VALIDA_SEM_MOVIMENTOS e BLOQUEADA_POR_DEPENDENCIA."""
        import csv
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as tmp_root:
            root_p = Path(tmp_root)
            tmp_in = root_p / "in_misto"
            tmp_out = root_p / "out_misto"
            tmp_in.mkdir(parents=True, exist_ok=True)
            tmp_out.mkdir(parents=True, exist_ok=True)

            # 1) TABELA_TAXAS_CONTRATUAIS: presente e válida (PROCESSADA)
            shutil.copy(self.raw_dir / "02_tabela_taxas_contratadas.xlsx", tmp_in / "02_tabela_taxas_contratadas.xlsx")

            # 2) ORBE_FECHAMENTO_PRINCIPAL: layout válido mas sem movimentos (VALIDA_SEM_MOVIMENTOS)
            f_orbe_vazio = tmp_in / "01_orbe_relatorio_comissoes_set2026.csv"
            with open(f_orbe_vazio, "w", encoding="utf-8", newline="") as fo:
                w = csv.writer(fo, delimiter=";")
                w.writerow([
                    "id_transacao", "data_movimento", "cod_estabelecimento", "nome_estabelecimento",
                    "tipo_lancamento", "modalidade", "qtd_parcelas", "bandeira", "valor_bruto",
                    "taxa_aplicada_pct", "valor_taxa", "valor_liquido", "id_referencia", "data_venda_original",
                ])

            # 3) EXTRATO_MERIDIANO: arquivo corrompido/layout inválido (INVALIDA) -> gera pendência e não zero silencioso!
            f_merid_invalido = tmp_in / "05b_extrato_banco_meridiano_cc90233_set2026.ofx"
            f_merid_invalido.write_text("ARQUIVO_CORROMPIDO_SEM_TAGS_OFX", encoding="utf-8")

            # 4) EXTRATO_AURORA: válido (PROCESSADA na Silver), mas bloqueado na conciliação pois Meridiano é inválido (BLOQUEADA_POR_DEPENDENCIA)
            shutil.copy(self.raw_dir / "05a_extrato_banco_aurora_cc4471_set2026.csv", tmp_in / "05a_extrato_banco_aurora_cc4471_set2026.csv")

            # 5) EMAIL_PONTE_CAMBIO: não copiado (AUSENTE)

            app = build_closing_graph()
            final_state = app.invoke({
                "data_dir": str(tmp_in),
                "output_dir_local": str(tmp_out),
                "output_dir_oficial": str(tmp_out),
                "competencia": "2026-09",
            })

            cob = final_state["cobertura_fontes"]
            self.assertEqual(cob["TABELA_TAXAS_CONTRATUAIS"]["estado"], "PROCESSADA")
            self.assertEqual(cob["ORBE_FECHAMENTO_PRINCIPAL"]["estado"], "VALIDA_SEM_MOVIMENTOS")
            self.assertEqual(cob["EXTRATO_MERIDIANO"]["estado"], "INVALIDA")
            self.assertEqual(cob["EXTRATO_AURORA"]["estado"], "BLOQUEADA_POR_DEPENDENCIA")
            self.assertEqual(cob["EMAIL_PONTE_CAMBIO"]["estado"], "AUSENTE")
            self.assertEqual(final_state["estado_tecnico"], "PARCIAL_COM_BLOQUEIOS")

            # Verifica que a fonte inválida e o bloqueio de dependência geraram pendências formais com responsável
            with open(tmp_out / "pendencias.csv", "r", encoding="utf-8") as fp:
                pends = list(csv.DictReader(fp, delimiter=";"))
            tipos_pends = {p["tipo"] for p in pends}
            self.assertIn("FONTE_INVALIDA_OU_LAYOUT_DESCONHECIDO", tipos_pends)
            self.assertIn("FONTE_DEPENDENTE_AUSENTE", tipos_pends)


if __name__ == "__main__":
    unittest.main()

